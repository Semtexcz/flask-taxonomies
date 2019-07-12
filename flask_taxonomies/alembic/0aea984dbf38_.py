"""empty message

Revision ID: 0aea984dbf38
Revises:
Create Date: 2019-06-21 10:48:07.706153

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0aea984dbf38'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('taxonomy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('taxonomy_term',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(length=64), nullable=True),
    sa.Column('title', sa.JSON(), nullable=True),
    sa.Column('extra_data', sa.JSON(), nullable=True),
    sa.Column('taxonomy_id', sa.Integer(), nullable=True),
    sa.Column('tree_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('lft', sa.Integer(), nullable=False),
    sa.Column('rgt', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['taxonomy_term.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['taxonomy_id'], ['taxonomy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('taxonomy_term')
    op.drop_table('taxonomy')
    # ### end Alembic commands ###
