# -*- coding: utf-8 -*-
#

"""Module tests."""

from __future__ import absolute_import, print_function

import pytest
from flask import Flask

from flask_taxonomies import FlaskTaxonomies
from flask_taxonomies.ext import _FlaskTaxonomiesState
from flask_taxonomies.proxies import current_flask_taxonomies


def test_version():
    """Test version import."""
    from flask_taxonomies import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = FlaskTaxonomies(app)
    assert 'flask-taxonomies' in app.extensions

    app = Flask('testapp')
    ext = FlaskTaxonomies()
    assert 'flask-taxonomies' not in app.extensions
    ext.init_app(app)
    assert 'flask-taxonomies' in app.extensions


def test_state():
    app = Flask('testapp')
    ext = FlaskTaxonomies(app)
    ext.init_app(app)

    state = app.extensions['flask-taxonomies']

    assert isinstance(state, _FlaskTaxonomiesState)
    assert callable(state.permission_factory)


def test_alembic(app, db):
    """Test alembic recipes."""
    ext = app.extensions['invenio-db']

    if db.engine.name == 'sqlite':
        raise pytest.skip('Upgrades are not supported on SQLite.')

    assert not ext.alembic.compare_metadata()
    db.drop_all()
    ext.alembic.upgrade()

    assert not ext.alembic.compare_metadata()
