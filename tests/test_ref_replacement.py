import pytest
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTEGER, JSONB, TIMESTAMP, UUID
from sqlalchemy.engine import create_engine
from sqlalchemy_utils import database_exists, create_database

from flask_taxonomies.cli import db_engine, load_tables


@pytest.fixture()
def test_db():
    # engine = create_engine('sqlite://')
    engine = create_engine("postgresql://oarepo:oarepo@localhost:5432/test")
    if not database_exists(engine.url):
        create_database(engine.url)
    metadata = sa.MetaData()
    records_metadata = sa.Table('records_metadata', metadata,
                                sa.Column('created', TIMESTAMP),
                                sa.Column('updated', TIMESTAMP),
                                sa.Column('id', UUID, primary_key=True),
                                sa.Column('json', JSONB, nullable=False),
                                sa.Column('version_id', INTEGER, nullable=False)
                                )
    metadata.create_all(engine)
    return engine


@pytest.fixture
def engine():
    return db_engine()


def test_db_connect(engine):
    conn = engine.connect()
    assert conn.connection.is_valid
    conn.close()


def test_load_tables(test_db):
    tables = load_tables(test_db)
    assert isinstance(tables["records_metadata"], sa.Table)
