"""empty message

Revision ID: 27d7c6ff4ee2
Revises: 2d5a93595e77
Create Date: 2022-10-31 09:20:18.129202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27d7c6ff4ee2'
down_revision = '2d5a93595e77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('area_id', sa.Integer(), nullable=True))
    op.drop_column('venue', 'city')
    op.drop_column('venue', 'state')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('venue', sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('venue', 'area_id')
    # ### end Alembic commands ###