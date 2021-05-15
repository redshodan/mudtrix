from mautrix.client.state_store.sqlalchemy import RoomState, UserProfile

from .portal import Portal
from .puppet import Puppet
from .user import User, UserPortal


def init(db_engine) -> None:
    for table in Portal, User, Puppet, UserProfile, RoomState, UserPortal:
        table.db = db_engine
        table.t = table.__table__
        table.c = table.t.c
        table.column_names = table.c.keys()
