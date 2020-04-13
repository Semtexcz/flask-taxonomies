"""Initial version

Revision ID: c4f7f7b28eb4
Revises: 
Create Date: 2020-04-13 12:41:27.109154

"""
from alembic import op
import sqlalchemy as sa
import flask_taxonomies.fields
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c4f7f7b28eb4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('taxonomy_taxonomy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=256), nullable=True),
    sa.Column('url', sa.String(length=1024), nullable=True),
    sa.Column('extra_data', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_taxonomy_taxonomy_code'), 'taxonomy_taxonomy', ['code'], unique=True)
    op.create_index(op.f('ix_taxonomy_taxonomy_url'), 'taxonomy_taxonomy', ['url'], unique=True)
    op.create_table('taxonomy_term',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', flask_taxonomies.fields.SlugType().with_variant(flask_taxonomies.fields.PostgresSlugType(), 'postgresql'), nullable=True),
    sa.Column('extra_data', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('taxonomy_id', sa.Integer(), nullable=True),
    sa.Column('busy_count', sa.Integer(), nullable=True),
    sa.Column('obsoleted_by_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('alive', 'deleted', 'delete_pending', name='termstatusenum'), nullable=False),
    sa.ForeignKeyConstraint(['obsoleted_by_id'], ['taxonomy_term.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['taxonomy_term.id'], ),
    sa.ForeignKeyConstraint(['taxonomy_id'], ['taxonomy_taxonomy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('index_term_slug', 'taxonomy_term', ['slug'], unique=False, postgresql_using='gist')
    op.create_index(op.f('ix_taxonomy_term_slug'), 'taxonomy_term', ['slug'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_taxonomy_term_slug'), table_name='taxonomy_term')
    op.drop_index('index_term_slug', table_name='taxonomy_term')
    op.drop_table('taxonomy_term')
    op.drop_index(op.f('ix_taxonomy_taxonomy_url'), table_name='taxonomy_taxonomy')
    op.drop_index(op.f('ix_taxonomy_taxonomy_code'), table_name='taxonomy_taxonomy')
    op.drop_table('taxonomy_taxonomy')
    # ### end Alembic commands ###
