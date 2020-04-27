import enum
import logging

import sqlalchemy.dialects
from flask import current_app
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Index, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.utils import cached_property

from flask_taxonomies.constants import *
from flask_taxonomies.fields import SlugType, PostgresSlugType
from flask_taxonomies.proxies import current_flask_taxonomies

logger = logging.getLogger('taxonomies')


class TaxonomyError(Exception):
    pass


Base = declarative_base()


def _cast_set(x, return_none=False):
    if x is None and return_none:
        return None
    if not x:
        return set()
    return set(x)


class Representation:
    KNOWN_FEATURES = {
        PRETTY_PRINT,
        INCLUDE_ANCESTORS,
        INCLUDE_URL,
        INCLUDE_DATA,
        INCLUDE_ID,
        INCLUDE_DESCENDANTS
    }

    def __init__(self, representation, include=None, exclude=None, selectors=None, options=None):
        self.representation = representation

        self._include = include
        self._exclude = exclude
        self._selectors = selectors
        self._options = options

    @cached_property
    def include(self):
        return _cast_set(self._include) | _cast_set(self._config['include'])

    @cached_property
    def exclude(self):
        return _cast_set(self._exclude) | _cast_set(self._config['exclude'])

    @cached_property
    def selectors(self):
        config_selectors = _cast_set(self._config['selectors'], return_none=True)
        self_selectors = _cast_set(self._selectors, return_none=True)

        if config_selectors is not None:
            if self_selectors is not None:
                return self_selectors | config_selectors
            else:
                return config_selectors
        elif self_selectors is not None:
            return self_selectors

    @cached_property
    def options(self):
        return self._options or self._config['options'] or {}

    @cached_property
    def _config(self):
        return current_app.config['FLASK_TAXONOMIES_REPRESENTATION'].get(
            self.representation, {
                'include': set(),
                'exclude': set(),
                'selectors': None,
                'options': {}
            })

    def __contains__(self, item):
        return item in self.include and item not in self.exclude

    def as_query(self):
        ret = {
            'representation:representation': self.representation,
        }
        if self.include:
            ret['representation:include'] = list(self.include)
        if self.exclude:
            ret['representation:exclude'] = list(self.exclude)
        if self.selectors:
            ret['representation:selectors'] = list(self.selectors)
        if self.options:
            for k, v in self.options.items():
                ret['representation:' + k] = str(v)
        return ret

    def copy(self, representation=None, include=None, exclude=None, selectors=None, options=None):
        return Representation(representation or self.representation,
                              include or self.include, exclude or self.exclude,
                              selectors or self.selectors,
                              options or self.options)

    def extend(self, include=None, exclude=None, selectors=None, options=None):
        if include:
            include = self.include | set(include)
        else:
            include = self.include
        if exclude:
            exclude = self.exclude | set(exclude)
        else:
            exclude = self.exclude
        if selectors:
            selectors = set(self.selectors or []) | set(selectors)
        else:
            selectors = self.selectors
        if options:
            options = {**self.options, **options}
        else:
            options = {**self.options}
        return Representation(self.representation, include, exclude, selectors, options)


DEFAULT_REPRESENTATION = Representation('representation')
PRETTY_REPRESENTATION = Representation('representation', include=[PRETTY_PRINT])


class Taxonomy(Base):
    __tablename__ = 'taxonomy_taxonomy'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(256), unique=True, index=True)
    url = Column(String(1024), unique=True, index=True)
    """
    Custom url of the taxonomy. If not set, the url is supposed to be 
    <FLASK_TAXONOMIES_SERVER_NAME or SERVER_NAME>/api/2.0/taxonomies/<name>
    """
    extra_data = Column(JSON().with_variant(
        sqlalchemy.dialects.postgresql.JSONB, 'postgresql'))
    terms = relationship("TaxonomyTerm", cascade="all, delete", lazy="dynamic")

    def __str__(self):
        return 'Taxonomy[{}]'.format(self.code)

    def __repr__(self):
        return str(self)

    def json(self, representation=DEFAULT_REPRESENTATION):
        resp = {
            'code': self.code,
        }
        links = {}
        if INCLUDE_URL in representation:
            links['self'] = current_flask_taxonomies.taxonomy_url(self)
            if self.url:
                links['custom'] = self.url
        if INCLUDE_DESCENDANTS_URL in representation:
            links['tree'] = current_flask_taxonomies.taxonomy_url(self, descendants=True)

        if links:
            resp['links'] = links

        if INCLUDE_ID in representation:
            resp['id'] = self.id
        if INCLUDE_DATA in representation and self.extra_data:
            resp.update(current_flask_taxonomies.extract_data(representation, self))
        return resp


class TermStatusEnum(enum.Enum):
    alive = 'A'
    """
    Alive taxonomy terms
    """

    deleted = 'D'
    """
    Taxonomy terms that have been deleted but should be kept in the database
    """

    delete_pending = 'd'
    """
    Taxonomy term that is in process of deletion. When its busy_count reaches 0,
    it will be permanently removed from the database
    """


class TaxonomyTerm(Base):
    __tablename__ = 'taxonomy_term'

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(SlugType(1024).with_variant(PostgresSlugType(), 'postgresql'),
                  unique=False, index=True)
    extra_data = Column(JSON().with_variant(
        sqlalchemy.dialects.postgresql.JSONB, 'postgresql'))
    level = Column(Integer)

    parent_id = Column(Integer, ForeignKey(__tablename__ + '.id'))
    parent = relationship("TaxonomyTerm", back_populates="children",
                          remote_side=id, foreign_keys=parent_id)
    children = relationship("TaxonomyTerm", back_populates="parent",
                            lazy="dynamic", foreign_keys=parent_id,
                            order_by=slug)

    taxonomy_id = Column(Integer, ForeignKey(Taxonomy.__tablename__ + '.id'))
    taxonomy = relationship("Taxonomy", back_populates="terms")
    taxonomy_code = Column(String(256))

    busy_count = Column(Integer, default=0)
    obsoleted_by_id = Column(Integer, ForeignKey(__tablename__ + '.id'))
    obsoleted_by = relationship("TaxonomyTerm", back_populates="obsoletes",
                                remote_side=id, foreign_keys=obsoleted_by_id)
    obsoletes = relationship("TaxonomyTerm", back_populates="obsoleted_by",
                             lazy="dynamic", foreign_keys=obsoleted_by_id)
    status = Column(Enum(TermStatusEnum), default=TermStatusEnum.alive, nullable=False)

    __table_args__ = (
        Index('index_term_slug', slug, postgresql_using="gist"),
        UniqueConstraint(taxonomy_id, slug, name='unique_taxonomy_slug')
    )

    @property
    def parent_slug(self):
        if '/' in self.slug:
            return self.slug.rsplit('/')[0]
        return None

    def __str__(self):
        return 'TaxonomyTerm[tax {}, lev {}, slug {}]'.format(
            self.taxonomy.code, self.level, self.slug)

    def __repr__(self):
        return str(self)

    def json(self, representation=DEFAULT_REPRESENTATION):
        resp = {}
        if INCLUDE_SLUG in representation:
            resp['slug'] = self.taxonomy_code + '/' + self.slug
        if INCLUDE_LEVEL in representation:
            resp['level'] = self.level

        links = {}
        if INCLUDE_URL in representation:
            links['self'] = current_flask_taxonomies.taxonomy_term_url(self)

        if INCLUDE_DESCENDANTS_URL in representation:
            links['tree'] = current_flask_taxonomies.taxonomy_term_url(self, descendants=True)

        if links:
            resp['links'] = links

        if INCLUDE_ID in representation:
            resp['id'] = self.id
        if INCLUDE_DATA in representation and self.extra_data:
            resp.update(current_flask_taxonomies.extract_data(representation, self))
        return resp
