import json
from urllib.parse import urlparse, urlunparse

import click
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
@click.option('-h', '--host', help='New host in $ref statement')
@click.option('-d', '--dialect', default='postgresql', help='e.g. (Postgres, MySQL, Oracle etc.')
@click.option('-D', '--database', default='oarepo', help='Name of database')
@click.option('-U', '--username', default='oarepo', help='Username')
@click.option('-H', '--db_host', default='localhost', help='Database server host')
@click.option('-v', '--verbose', is_flag=True)
@click.password_option()
def replace_ref_host(host, dialect, database, username, db_host, password, verbose):
    engine = db_engine(
        dialect=dialect, database=database, username=username, host_=db_host, password=password)
    conn = db_connect(engine)
    print("Loading database tables...")
    table = load_tables(engine)["records_metadata"]
    print("Loading data...")
    data = load_data(conn, table)

    i = 0
    for row in data:
        i += 1
        id_ = row[2]
        json_ = row[3]
        new_json = parse_json(json_, host)
        database_update(table, conn, id_, new_json)
        print(f"{i}.: Record number {id_} was updated")
        if verbose:
            print("old json: ", json_)
            print("new_json: ", new_json, "\n\n")


def db_engine(dialect: str = 'postgresql', database: str = 'oarepo', username: str = 'oarepo',
              password: str = 'oarepo', host_: str = 'localhost', port: str = '5432') -> object:
    """
    Return SQLAlchemy engine
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
            elif isinstance(v, dict) and "$ref" in v:
                new_json[k] = replace_host(v, new_host)
            else:
                new_json[k] = v
        else:
            new_json[k] = v
    return new_json


def database_update(table, connection, id_, new_json):
    stmt = table.update().where(table.c.id == str(id_)).values(json=new_json)
    connection.execute(stmt)
