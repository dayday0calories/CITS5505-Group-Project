"""Initial migration

Revision ID: 802f83ad9167
Revises: 
Create Date: 2024-05-17 15:37:19.101381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '802f83ad9167'
down_revision = None
branch_labels = None
depends_on = None



def upgrade():
    op.execute("UPDATE post SET likes = 0")
    op.execute("UPDATE reply SET likes = 0")


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
   op.drop_table('notification')

    # ### end Alembic commands ###
