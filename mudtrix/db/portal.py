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
from typing import Optional, Iterator

from sqlalchemy import Column, Text, SmallInteger, Boolean, false, or_

from mautrix.types import RoomID
from mautrix.util.db import Base


class Portal(Base):
    __tablename__ = "portal"

    # Hangouts chat information
    gid: str = Column(Text, primary_key=True)
    receiver: str = Column(Text, primary_key=True)
    conv_type: int = Column(SmallInteger, nullable=False)
    other_user_id: str = Column(Text, nullable=True)

    # Matrix portal information
    mxid: RoomID = Column(Text, unique=True, nullable=True)
    encrypted: bool = Column(Boolean, nullable=False, server_default=false())

    # Hangouts chat metadata
    name = Column(Text, nullable=True)

    @classmethod
    def get_by_gid(cls, gid: str, receiver: str) -> Optional['Portal']:
        return cls._select_one_or_none(cls.c.gid == gid, or_(cls.c.receiver == receiver,
                                                             cls.c.receiver == ""))

    @classmethod
    def get_by_mxid(cls, mxid: RoomID) -> Optional['Portal']:
        return cls._select_one_or_none(cls.c.mxid == mxid)

    # @classmethod
    # def get_all_by_receiver(cls, receiver: str) -> Iterator['Portal']:
    #     return cls._select_all(cls.c.receiver == receiver,
    #                            cls.c.conv_type == hangouts.CONVERSATION_TYPE_ONE_TO_ONE)

    @classmethod
    def all(cls) -> Iterator['Portal']:
        return cls._select_all()
