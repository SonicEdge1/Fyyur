"""empty message

Revision ID: 24dc5d4bd4e1
Revises: 281489f1adb0
Create Date: 2021-07-01 15:42:30.957550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24dc5d4bd4e1'
down_revision = '281489f1adb0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('artist', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('artist', 'website_link')
    # ### end Alembic commands ###
