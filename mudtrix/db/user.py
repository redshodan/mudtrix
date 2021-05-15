# mautrix-hangouts - A Matrix-Hangouts puppeting bridge
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Optional, Iterable

from sqlalchemy import Column, Text, ForeignKeyConstraint, Boolean
from sqlalchemy.sql import expression

from mautrix.types import UserID, RoomID
from mautrix.util.db import Base


class User(Base):
    __tablename__ = "user"

    mxid: UserID = Column(Text, primary_key=True)
    gid: str = Column(Text, nullable=True)
    refresh_token: str = Column(Text, nullable=True)
    notice_room: RoomID = Column(Text, nullable=True)

    @classmethod
    def all(cls) -> Iterable['User']:
        return cls._select_all()

    @classmethod
    def get_by_gid(cls, gid: str) -> Optional['User']:
        return cls._select_one_or_none(cls.c.gid == gid)

    @classmethod
    def get_by_mxid(cls, mxid: UserID) -> Optional['User']:
        return cls._select_one_or_none(cls.c.mxid == mxid)

    @property
    def portals(self) -> Iterable['UserPortal']:
        rows = self.db.execute(UserPortal.t.select().where(UserPortal.c.user == self.gid))
        for row in rows:
            yield UserPortal.scan(row)

    @portals.setter
    def portals(self, portals: Iterable['UserPortal']) -> None:
        with self.db.begin() as conn:
            conn.execute(UserPortal.t.delete().where(UserPortal.c.user == self.gid))
            insert_portals = [{
                "user": user,
                "portal": portal,
                "portal_receiver": portal_receiver,
                "in_community": in_community,
            } for user, portal, portal_receiver, in_community in portals]
            if insert_portals:
                conn.execute(UserPortal.t.insert(), insert_portals)

    def delete(self) -> None:
        super().delete()
        self.portals = []


class UserPortal(Base):
    __tablename__ = "user_portal"

    user: str = Column(Text, primary_key=True)
    portal: str = Column(Text, primary_key=True)
    portal_receiver: str = Column(Text, primary_key=True)
    in_community: bool = Column(Boolean, nullable=False, server_default=expression.false())

    __table_args__ = (ForeignKeyConstraint(("portal", "portal_receiver"),
                                           ("portal.gid", "portal.receiver"),
                                           onupdate="CASCADE", ondelete="CASCADE"),)
