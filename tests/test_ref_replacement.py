import uuid
import json

import pytest
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTEGER, JSONB, TIMESTAMP, UUID
from sqlalchemy.engine import create_engine
from sqlalchemy_utils import database_exists, create_database

from flask_taxonomies.cli import db_engine, load_tables, load_data


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
                    'name': 'This Master Thesis is focused on analysis of media response to '
                            'editions '
                            'Fresh and Raketa of publishing house Labyrint in the context of '
                            'history '
                            ' of publishing practice in the Czech Republic in the nineties.'
                            ' It also discusses contemporary literature for children and youth.'
                            ' Thesis studies critical media response to three particular books'
                            ' from studied editions Tajemství oblázkové hory by Bára Dočkalová,'
                            ' Robinson by Petr Sís and Plyš by Michal Hvorecký.'
                            ' Novel Plyš by Michal Hvorecký was covered the most in the media. '
                            'The smallest number of articles was published about'
                            ' Tajemství oblázkové hory by Bára Dočkalová.'
                            ' Even though it was nominated for Magnesia Litera Award,'
                            ' it did not win the price in the end. The closing part'
                            ' focuses on a unique project by publishing house Labyrint,'
                            ' a magazine for children called Raketa.'
                            ' Media attention is focused on creators'
                            ' of magazine, either it is the owner of publishing house Labyrint '
                            'Joachim Dvořák or its chief editors Johana Švejdíková and Radana'
                            ' Litošová.'
                            'Critical reflection is rare, there are mostly short notes '
                            'recommending '
                            ' buying'
                            ' the magazine or describing a new issue. There is a broad spectrum of'
                            ' media chosen for'
                            ' this analysis, from news media to cultural and literary periodical '
                            'such as Tvar, Host, A2 and catalog Nejlepší knihy dětem.',
                    'lang': 'eng'},
                dict(name='Diplomová práce se zabývá analýzou mediálního ohlasu edic Fresh a '
                          'Raketa '
                          'nakladatelství Labyrint v\n                kontextu vývoje '
                          'nakladatelské '
                          'praxe v České republice v devadesátých letech. Věnuje se také '
                          'současné\n '
                          'literatuře pro děti a mládež. Součástí práce je kritický '
                          'ohlas na tři konkrétní díla, jedná se o knihy\n                ze '
                          'zkoumaných edic Tajemství oblázkové hory Báry Dočkalové, Robinson '
                          'Petra '
                          'Síse a Plyš Michala\n                Hvoreckého. Nejčastěji bylo v '
                          'médiích referováno o románu Plyš slovenského spisovatele Michala\n '
                          'Hvoreckého. Nejméně příspěvků se věnovalo debutu Báry Dočkalové '
                          'Tajemství oblázkové hory, který byl sice\n                nominován '
                          'na '
                          'cenu Magnesia Litera 2019, nominaci ale neproměnil. Závěrečná část se '
                          'věnuje unikátnímu\n                projektu nakladatelství Labyrint, '
                          'kterým je dětský časopis Raketa. Mediální pozornost přitahují '
                          'zejména\n '
                          'jeho tvůrci, ať už jde o majitele nakladatelství Joachima '
                          'Dvořáka nebo šéfredaktorky Johanu Švejdíkovou\n                a '
                          'Radanu '
                          'Litošovou. Kritická percepce časopisu se objevuje sporadicky, '
                          'jedná se '
                          'zejména o představení\n                časopisu nebo jeho doporučení. '
                          'Spektrum zkoumaných periodik je široké od zpravodajských webů a '
                          'deníků '
                          'až\n                po kulturní a literární periodika Tvar, Host, '
                          'A2 kulturní čtrnáctideník a katalog Nejlepší knihy dětem.', lang='cze')

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
            'defended': True})


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

    yield engine

    conn.close()
    metadata.drop_all(bind=engine)


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


def test_load_data(test_db, test_json):
    conn = test_db.connect()
    table = load_tables(test_db)["records_metadata"]
    data = load_data(conn, table)
    row = data.fetchone()
    assert row[3] == test_json
