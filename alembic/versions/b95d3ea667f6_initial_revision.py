"""initial revision

Revision ID: b95d3ea667f6
Revises: 
Create Date: 2021-03-14 20:38:46.981020

"""
from alembic import op
import sqlalchemy as sa
from mautrix.types import (PowerLevelStateEventContent as PowerLevels,
                           RoomEncryptionStateEventContent as EncryptionInfo)
from mautrix.client.state_store.sqlalchemy.mx_room_state import SerializableType


# revision identifiers, used by Alembic.
revision = 'b95d3ea667f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mx_room_state',
    sa.Column('room_id', sa.Text(), nullable=False),
    sa.Column('is_encrypted', sa.Boolean(), nullable=True),
    sa.Column('has_full_member_list', sa.Boolean(), nullable=True),
    sa.Column('encryption', SerializableType(EncryptionInfo), nullable=True),
    sa.Column('power_levels', SerializableType(SerializableType), nullable=True),
    sa.PrimaryKeyConstraint('room_id')
    )
    op.create_table('mx_user_profile',
    sa.Column('room_id', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Text(), nullable=False),
    sa.Column('membership', sa.Enum('JOIN', 'LEAVE', 'INVITE', 'BAN', 'KNOCK', name='membership'), nullable=False),
    sa.Column('displayname', sa.Text(), nullable=True),
    sa.Column('avatar_url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('room_id', 'user_id')
    )
    op.create_table('portal',
    sa.Column('gid', sa.Text(), nullable=False),
    sa.Column('receiver', sa.Text(), nullable=False),
    sa.Column('conv_type', sa.SmallInteger(), nullable=False),
    sa.Column('other_user_id', sa.Text(), nullable=True),
    sa.Column('mxid', sa.Text(), nullable=True),
    sa.Column('encrypted', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('gid', 'receiver'),
    sa.UniqueConstraint('mxid')
    )
    op.create_table('puppet',
    sa.Column('gid', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('name_set', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.Column('photo_url', sa.Text(), nullable=True),
    sa.Column('avatar_set', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.Column('matrix_registered', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.Column('custom_mxid', sa.Text(), nullable=True),
    sa.Column('access_token', sa.Text(), nullable=True),
    sa.Column('next_batch', sa.Text(), nullable=True),
    sa.Column('base_url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('gid')
    )
    op.create_table('user',
    sa.Column('mxid', sa.Text(), nullable=False),
    sa.Column('gid', sa.Text(), nullable=True),
    sa.Column('refresh_token', sa.Text(), nullable=True),
    sa.Column('notice_room', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('mxid')
    )
    op.create_table('user_portal',
    sa.Column('user', sa.Text(), nullable=False),
    sa.Column('portal', sa.Text(), nullable=False),
    sa.Column('portal_receiver', sa.Text(), nullable=False),
    sa.Column('in_community', sa.Boolean(), server_default=sa.text('0'), nullable=False),
    sa.ForeignKeyConstraint(['portal', 'portal_receiver'], ['portal.gid', 'portal.receiver'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user', 'portal', 'portal_receiver')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_portal')
    op.drop_table('user')
    op.drop_table('puppet')
    op.drop_table('portal')
    op.drop_table('mx_user_profile')
    op.drop_table('mx_room_state')
    # ### end Alembic commands ###