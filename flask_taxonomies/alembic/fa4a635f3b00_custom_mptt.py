#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Custom MPTT."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'fa4a635f3b00'
down_revision = 'e5848504dc5f'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('taxonomy_tree_id',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_taxonomy_tree_id'))
    )
    op.add_column('taxonomy_term', sa.Column('left', sa.Integer(), nullable=False))
    op.add_column('taxonomy_term', sa.Column('order', sa.Integer(), nullable=False))
    op.add_column('taxonomy_term', sa.Column('right', sa.Integer(), nullable=False))
    op.alter_column('taxonomy_term', 'tree_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_unique_constraint('uq_taxonomy_term_slug_parent', 'taxonomy_term', ['slug', 'parent_id'])
    op.create_unique_constraint('uq_taxonomy_term_slug_tree', 'taxonomy_term', ['slug', 'tree_id'])
    op.drop_constraint('uq_taxonomy_term_slug', 'taxonomy_term', type_='unique')
    op.drop_constraint('fk_taxonomy_term_parent_id_taxonomy_term', 'taxonomy_term', type_='foreignkey')
    op.create_foreign_key(op.f('fk_taxonomy_term_parent_id_taxonomy_term'), 'taxonomy_term', 'taxonomy_term', ['parent_id'], ['id'])
    op.drop_column('taxonomy_term', 'lft')
    op.drop_column('taxonomy_term', 'rgt')
    # ### end Alembic commands ###


def downgrade():
    """Downgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('taxonomy_term', sa.Column('rgt', sa.INTEGER(), nullable=False))
    op.add_column('taxonomy_term', sa.Column('lft', sa.INTEGER(), nullable=False))
    op.drop_constraint(op.f('fk_taxonomy_term_parent_id_taxonomy_term'), 'taxonomy_term', type_='foreignkey')
    op.create_foreign_key('fk_taxonomy_term_parent_id_taxonomy_term', 'taxonomy_term', 'taxonomy_term', ['parent_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('uq_taxonomy_term_slug', 'taxonomy_term', ['slug', 'parent_id'])
    op.drop_constraint('uq_taxonomy_term_slug_tree', 'taxonomy_term', type_='unique')
    op.drop_constraint('uq_taxonomy_term_slug_parent', 'taxonomy_term', type_='unique')
    op.alter_column('taxonomy_term', 'tree_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('taxonomy_term', 'right')
    op.drop_column('taxonomy_term', 'order')
    op.drop_column('taxonomy_term', 'left')
    op.drop_table('taxonomy_tree_id')
    # ### end Alembic commands ###
