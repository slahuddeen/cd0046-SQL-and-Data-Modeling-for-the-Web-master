"""empty message

Revision ID: 3ef74e55a8aa
Revises: c0195387fb8c
Create Date: 2022-11-03 12:57:23.664331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ef74e55a8aa'
down_revision = 'c0195387fb8c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###
