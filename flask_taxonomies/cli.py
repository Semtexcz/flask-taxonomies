import click
from urllib.parse import urlparse, urlunparse
import sqlalchemy as sa
from flask.cli import with_appcontext
from invenio_access import ActionSystemRoles, any_user
from invenio_db import db
from sqlalchemy.sql import select

#
# Taxonomies commands
#
from flask_taxonomies.models import Taxonomy
from flask_taxonomies.permissions import (
    taxonomy_create_all,
    taxonomy_delete_all,
    taxonomy_read_all,
    taxonomy_term_create_all,
    taxonomy_term_delete_all,
    taxonomy_term_move_all,
    taxonomy_term_read_all,
    taxonomy_term_update_all,
    taxonomy_update_all,
)


@click.group()
def taxonomies():
    """Taxonomies commands."""


#
# Taxonomies subcommands
#
@taxonomies.command('all-read')
@with_appcontext
def all_read():
    """Set permissions for everyone to read all taxonomies and taxonomy terms."""
    db.session.add(ActionSystemRoles.allow(taxonomy_read_all, role=any_user))
    db.session.add(ActionSystemRoles.allow(taxonomy_term_read_all, role=any_user))
    db.session.commit()


@taxonomies.command('all-modify')
@with_appcontext
def all_modify():
    """Set permissions for everyone to read all taxonomies and taxonomy terms."""
    db.session.add(ActionSystemRoles.allow(taxonomy_create_all, role=any_user))
    db.session.add(ActionSystemRoles.allow(taxonomy_update_all, role=any_user))
    db.session.add(ActionSystemRoles.allow(taxonomy_delete_all, role=any_user))
    db.session.add(ActionSystemRoles.allow(taxonomy_term_create_all, role=any_user))
    db.session.add(ActionSystemRoles.allow(taxonomy_term_update_all, role=any_user))
    db.session.add(ActionSystemRoles.allow(taxonomy_term_delete_all, role=any_user))
    db.session.add(ActionSystemRoles.allow(taxonomy_term_move_all, role=any_user))
    db.session.commit()


@taxonomies.command('import')
@click.argument('taxonomy_file')
@click.option('--int', 'int_conversions', multiple=True)
@click.option('--str', 'str_args', multiple=True)
@click.option('--drop/--no-drop', default=False)
@with_appcontext
def import_taxonomy(taxonomy_file, int_conversions, str_args, drop):
    from .import_export import import_taxonomy
    import_taxonomy(taxonomy_file, int_conversions, str_args, drop)


@taxonomies.command('list')
@with_appcontext
def list_taxonomies():
    for t in Taxonomy.taxonomies():
        print(t.code)


@taxonomies.command('delete')
@click.argument('code')
@with_appcontext
def delete_taxonomy(code):
    t = Taxonomy.get(code)
    db.session.delete(t)
    db.session.commit()


@taxonomies.command('replace-ref-host')
@click.option('-h', '--host', help='Replace host in $ref statements')
def replace_host(host):
    print(host)


# TODO: logger

# Connect to database
def db_engine(dialect: str = 'postgresql', database: str = 'oarepo', username: str = 'oarepo',
              password: str = 'oarepo', host_: str = 'localhost', port: str = '5432') -> object:
    """
    Return SQLAlchemy engine
    :return:
    :rtype:
    :return:
    :rtype:
    :param dialect:
    :param database:
    :param username:
    :param password:
    :param host_:
    :param port:
    :return: SQLAlchemy engine
    """
    # dialect + driver: // username: password @ host:port / database
    opts = f'{dialect}://{username}:{password}@{host_}:{port}/{database}'
    return sa.create_engine(opts)


def db_connect(engine):
    """
    Returns db connection
    :param engine:
    :type engine: SQLAlchemy engine
    :return: SQLAlchemy connection
    """
    return engine.connect()


def load_tables(engine):
    metadata = sa.MetaData()
    metadata.reflect(bind=engine)
    return metadata.tables


def load_data(connection, table):
    s = select([table])
    return connection.execute(s)


def replace_host(ref_object, new_host):
    url = urlparse(ref_object["$ref"])
    new_url = url._replace(netloc=new_host)
    return {'$ref': urlunparse(new_url)}


def parse_json(json_, new_host):
    new_json = {}
    for k, v in json_.items():
        if isinstance(v, (list, dict)):
            if isinstance(v, list):
                new_list = []
                for item in v:
                    if '$ref' in item:
                        new_list.append(replace_host(item, new_host))
                    else:
                        new_list.append(item)
                new_json[k] = new_list
            if isinstance(v, dict) and "$ref" in v:
                new_json[k] = replace_host(v, new_host)
        else:
            new_json[k] = v
    return new_json


# TODO: parsování JSON
# TODO: vyhledání všech $ref
# TODO: nahrazení hosta
# TODO: update databáze
# TODO: hlavní program - for cyklus
# TODO: ukončení databáze

if __name__ == "__main__":
    # engine = db_engine()
    # tables = load_tables(engine)
    # data = load_data(db_connect(engine), tables["records_metadata"])
    # row = data.fetchone()
    # json = row[3]
    # parse_json(json)
    # print(json)
    json = {'contributor':
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
            'defended': True}
    print(parse_json(json, '127.0.0.1:8080'))
