"""empty message

Revision ID: 43e2119c430
Revises: 4f4ba05970c
Create Date: 2015-07-12 13:16:34.572231

"""

# revision identifiers, used by Alembic.
revision = '43e2119c430'
down_revision = '4f4ba05970c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('adventures', sa.Column('disabled_on', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('adventures', 'disabled_on')
    ### end Alembic commands ###
