"""empty message

Revision ID: c0195387fb8c
Revises: 7968c7db0609
Create Date: 2022-11-03 11:58:47.690268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0195387fb8c'
down_revision = '7968c7db0609'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'website')
    op.drop_column('venue', 'seeking_talent')
    # ### end Alembic commands ###
