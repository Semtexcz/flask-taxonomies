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


# TODO: parsování JSON
# TODO: vyhledání všech $ref
# TODO: parsování URL
# TODO: nahrazení hosta
# TODO: update databáze
# TODO: hlavní program - for cyklus
# TODO: ukončení databáze

if __name__ == "__main__":
    engine = db_engine()
    tables = load_tables(engine)
    data = load_data(db_connect(engine), tables["records_metadata"])
    row = data.fetchone()
    json = row[3]
    parse_json(json)
    print(json)
