""" Add `scale` to Printer table.

Revision ID: d37b1524c3fc
Revises: 1ab329f328d9
Create Date: 2020-02-16 02:08:31.875238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd37b1524c3fc'
down_revision = '1ab329f328d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('printers', sa.Column('scale', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('printers') as batch:
        batch.drop_column('scale')
    # ### end Alembic commands ###
