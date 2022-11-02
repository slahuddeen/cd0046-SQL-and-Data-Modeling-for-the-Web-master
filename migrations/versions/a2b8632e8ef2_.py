"""empty message

Revision ID: a2b8632e8ef2
Revises: 9687044c7352
Create Date: 2022-10-31 11:32:57.268348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2b8632e8ef2'
down_revision = '9687044c7352'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('num_upcoming_shows', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'num_upcoming_shows')
    # ### end Alembic commands ###