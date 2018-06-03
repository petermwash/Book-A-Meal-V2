"""empty message

Revision ID: f6e71036c35c
Revises: 
Create Date: 2018-06-01 17:02:39.990956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6e71036c35c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=500), nullable=False),
    sa.Column('blacklisted_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('meals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('m_name', sa.String(length=200), nullable=True),
    sa.Column('category', sa.String(length=200), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('menus',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('m_name', sa.String(length=200), nullable=False),
    sa.Column('category', sa.String(length=200), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('day', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('meal_name', sa.String(length=75), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('owner', sa.String(length=75), nullable=False),
    sa.Column('ordered_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=75), nullable=False),
    sa.Column('f_name', sa.String(length=75), nullable=False),
    sa.Column('l_name', sa.String(length=75), nullable=False),
    sa.Column('u_name', sa.String(length=75), nullable=False),
    sa.Column('email', sa.String(length=75), nullable=False),
    sa.Column('password', sa.String(length=225), nullable=False),
    sa.Column('type_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('u_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('orders')
    op.drop_table('menus')
    op.drop_table('meals')
    op.drop_table('blacklist_tokens')
    # ### end Alembic commands ###
