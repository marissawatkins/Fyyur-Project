"""empty message

Revision ID: 275603016c52
Revises: f278cdb34763
Create Date: 2020-02-24 14:38:02.749051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '275603016c52'
down_revision = 'f278cdb34763'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('shows', 'image_link')
    op.drop_column('shows', 'city')
    op.drop_column('shows', 'name')
    op.drop_column('shows', 'facebook_link')
    op.drop_column('shows', 'seeking_description')
    op.drop_column('shows', 'website')
    op.drop_column('shows', 'address')
    op.drop_column('shows', 'state')
    op.drop_column('shows', 'genres')
    op.drop_column('shows', 'phone')
    op.drop_column('shows', 'seeking_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('shows', sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('address', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('website', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('seeking_description', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('facebook_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('shows', sa.Column('image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
