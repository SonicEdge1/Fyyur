"""empty message

Revision ID: 896a153b9f6c
Revises: a35c096f4326
Create Date: 2021-06-30 10:44:55.287683

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '896a153b9f6c'
down_revision = 'a35c096f4326'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.drop_column('artist', 'genres3')
    op.add_column('venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.drop_column('venue', 'genres3')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres3', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_column('venue', 'genres')
    op.add_column('artist', sa.Column('genres3', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))
    op.drop_column('artist', 'genres')
    # ### end Alembic commands ###
