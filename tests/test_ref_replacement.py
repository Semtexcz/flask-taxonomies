import json
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTEGER, JSONB, TIMESTAMP, UUID
from sqlalchemy.engine import create_engine
from sqlalchemy_utils import create_database, database_exists

from flask_taxonomies.cli import (
    database_update,
    db_engine,
    load_data,
    load_tables,
    parse_json,
    replace_host,
)


@pytest.fixture()
def ref_object():
    return {'$ref': 'https://localhost/api/taxonomies/subject/PSH7020'}


@pytest.fixture()
def test_json():
    return json.dumps(
        {'contributor':
            [
                {'name': 'Čeňková, Jana', 'role': 'advisor'},
                {'name': 'Malý, Radek', 'role': 'referee'}
            ],
            'identifier':
                [
                    {
                        'type': 'originalRecord',
                        'value': 'http://hdl.handle.net/20.500.11956/107892'
                    },
                    {'type': 'nusl', 'value': 'http://www.nusl.cz/ntk/nusl-398853'},
                    {
                        'type': 'originalOAI',
                        'value': 'oai:dspace.cuni.cz:20.500.11956/107892'
                    },
                    {
                        'type': 'nuslOAI',
                        'value': 'oai:invenio.nusl.cz:398853'
                    }
                ],
            'modified': '2019-07-26T09:16:38',
            'creator': [
                {'name': 'Kubiková, Karolína'}],
            'accessRights': 'open',
            'abstract': [
                {
                    'name': 'Test',
                    'lang': 'eng'},
                {
                    'name': 'Test',
                    "lang": "cze"
                }

            ],
            'subject': [
                {'$ref': 'https://localhost/api/taxonomies/subject/PSH7020'},
                {'$ref': 'https://localhost/api/taxonomies/subject/PSH7034'}
            ],
            'keywords': [
                {'name': 'Labyrint', 'lang': 'cze'},
                {'name': 'edice', 'lang': 'cze'},
                {'name': 'mediální ohlas', 'lang': 'cze'},
                {'name': 'Literature for Children and Youth', 'lang': 'eng'},
                {'name': 'publishing house', 'lang': 'eng'}, {'name': 'Labyrint', 'lang': 'eng'},
                {'name': 'edition', 'lang': 'eng'}, {'name': 'media response', 'lang': 'eng'}],
            'id': '398853',
            'provider': {
                '$ref': 'https://localhost/api/taxonomies/provider/univerzita_karlova_v_praze'},
            'doctype': {'$ref': 'https://localhost/api/taxonomies/doctype/diplomove_prace'},
            'degreeGrantor': [
                {'$ref': 'https://localhost/api/taxonomies/universities/katedra_zurnalistiky'}],
            'title': [{'name': 'Nakladatelství Labyrint a mediální reflexe edic Fresh a Raketa',
                       'lang': 'cze'}],
            'accessibility': [{'name': 'Dostupné v digitálním repozitáři UK.', 'lang': 'cze'},
                              {'name': 'Available in the Charles University Digital Repository.',
                               'lang': 'eng'}],
            'dateAccepted': '2019-06-20',
            'language': [{'$ref': 'https://localhost/api/taxonomies/languages/cze'}],
            'defended': True}, ensure_ascii=False)


@pytest.fixture()
def parsed_json():
    return json.dumps(
        {'contributor':
            [
                {'name': 'Čeňková, Jana', 'role': 'advisor'},
                {'name': 'Malý, Radek', 'role': 'referee'}
            ],
            'identifier':
                [
                    {
                        'type': 'originalRecord',
                        'value': 'http://hdl.handle.net/20.500.11956/107892'
                    },
                    {'type': 'nusl', 'value': 'http://www.nusl.cz/ntk/nusl-398853'},
                    {
                        'type': 'originalOAI',
                        'value': 'oai:dspace.cuni.cz:20.500.11956/107892'
                    },
                    {
                        'type': 'nuslOAI',
                        'value': 'oai:invenio.nusl.cz:398853'
                    }
                ],
            'modified': '2019-07-26T09:16:38',
            'creator': [
                {'name': 'Kubiková, Karolína'}],
            'accessRights': 'open',
            'abstract': [
                {
                    'name': 'Test',
                    'lang': 'eng'},
                {
                    'name': 'Test',
                    "lang": "cze"
                }

            ],
            'subject': [
                {'$ref': 'https://127.0.0.1:8080/api/taxonomies/subject/PSH7020'},
                {'$ref': 'https://127.0.0.1:8080/api/taxonomies/subject/PSH7034'}
            ],
            'keywords': [
                {'name': 'Labyrint', 'lang': 'cze'},
                {'name': 'edice', 'lang': 'cze'},
                {'name': 'mediální ohlas', 'lang': 'cze'},
                {'name': 'Literature for Children and Youth', 'lang': 'eng'},
                {'name': 'publishing house', 'lang': 'eng'}, {'name': 'Labyrint', 'lang': 'eng'},
                {'name': 'edition', 'lang': 'eng'}, {'name': 'media response', 'lang': 'eng'}],
            'id': '398853',
            'provider': {
                '$ref': 'https://127.0.0.1:8080/api/taxonomies/provider'
                        '/univerzita_karlova_v_praze'},
            'doctype': {'$ref': 'https://127.0.0.1:8080/api/taxonomies/doctype/diplomove_prace'},
            'degreeGrantor': [
                {
                    '$ref': 'https://127.0.0.1:8080/api/taxonomies/universities'
                            '/katedra_zurnalistiky'}],
            'title': [{'name': 'Nakladatelství Labyrint a mediální reflexe edic Fresh a Raketa',
                       'lang': 'cze'}],
            'accessibility': [{'name': 'Dostupné v digitálním repozitáři UK.', 'lang': 'cze'},
                              {'name': 'Available in the Charles University Digital Repository.',
                               'lang': 'eng'}],
            'dateAccepted': '2019-06-20',
            'language': [{'$ref': 'https://127.0.0.1:8080/api/taxonomies/languages/cze'}],
            'defended': True}, ensure_ascii=False)


@pytest.fixture()
def test_db(test_json):
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
    # insert test data
    stmt = records_metadata.insert().values(
        created='2019-11-22 06:01:06.538572',
        updated='2019-11-22 06:01:06.538572',
        id=str(uuid.uuid4()),
        json=test_json,
        version_id=1)
    conn = engine.connect()
    conn.execute(stmt)

    yield engine, conn

    conn.close()
    metadata.drop_all(bind=engine)


@pytest.fixture
def engine():
    return db_engine()


def test_db_engine():
    return db_engine()


def test_db_connect(engine):
    conn = engine.connect()
    assert conn.connection.is_valid
    conn.close()


def test_db_connect_2():
    engine = db_engine(username="blbost")
    with pytest.raises(sa.exc.OperationalError):
        conn = engine.connect()


def test_load_tables(test_db):
    tables = load_tables(test_db[0])
    assert isinstance(tables["records_metadata"], sa.Table)


def test_load_data(test_db, test_json):
    table = load_tables(test_db[0])["records_metadata"]
    data = load_data(test_db[1], table)
    row = data.fetchone()
    assert row[3] == test_json


def test_replace_host(ref_object):
    assert replace_host(ref_object, '127.0.0.1:8080') == {
        "$ref": "https://127.0.0.1:8080/api/taxonomies/subject/PSH7020"
    }


def test_parse_json(test_json, parsed_json):
    json_ = json.loads(test_json)
    parsed_json = json.loads(parsed_json)
    assert parse_json(json_, '127.0.0.1:8080') == parsed_json


def test_database_update(test_db, parsed_json):
    parsed_json = json.loads(parsed_json)
    table = load_tables(test_db[0])["records_metadata"]
    data = load_data(test_db[1], table)
    row = data.fetchone()
    id_ = row[2]
    database_update(table, test_db[1], id_, parsed_json)

    updated_data = load_data(test_db[1], table)
    updated_row = updated_data.fetchone()
    print(updated_row[3])
    assert updated_row[3] == parsed_json

# TODO: writer test for replace_ref_host http://click.palletsprojects.com/en/5.x/testing/
# def test_replace_ref_host(test_db):
#     replace_ref_host(
#         '127.0.0.1:8080', 'postgres', 'test', 'oarepo', 'localhost', 'oarepo', True)
