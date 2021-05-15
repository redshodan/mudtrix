from typing import Iterable, Awaitable

from mautrix.bridge import BasePuppet
from mautrix.types import RoomID, UserID, ContentURI, SyncToken

from .config import Config

config: Config


class Puppet(BasePuppet):
    def __init__(self, *args, **kwargs):
        print(f"Puppet(*args={args} **kwargs={kwargs})")

    @classmethod
    async def get_by_mxid(cls, mxid: UserID, create: bool = True):
        gid = cls.get_id_from_mxid(mxid)
        if gid:
            return cls.get_by_gid(gid, create)

        return None

    @classmethod
    def get_id_from_mxid(cls, mxid: UserID):
        prefix = cls._mxid_prefix
        suffix = cls._mxid_suffix
        if mxid[:len(prefix)] == prefix and mxid[-len(suffix):] == suffix:
            return mxid[len(prefix):-len(suffix)]
        return None


def init(context) -> Iterable[Awaitable[None]]:
    global config
    print("Puppet.init({context})")
    Puppet.az, config, Puppet.loop = context.core
    Puppet.mx = context.mx
    username_template = config["bridge.username_template"].lower()
    index = username_template.index("{userid}")
    length = len("{userid}")
    Puppet.hs_domain = config["homeserver"]["domain"]
    Puppet._mxid_prefix = f"@{username_template[:index]}"
    Puppet._mxid_suffix = f"{username_template[index + length:]}:{Puppet.hs_domain}"
