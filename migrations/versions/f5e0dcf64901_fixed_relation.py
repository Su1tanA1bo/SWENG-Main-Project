"""fixed relation

Revision ID: f5e0dcf64901
Revises: ebf21e3fc509
Create Date: 2022-11-21 13:56:55.094141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5e0dcf64901'
down_revision = 'ebf21e3fc509'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('repo_member',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('repo_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['repo_id'], ['repository.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('repo_member')
    # ### end Alembic commands ###