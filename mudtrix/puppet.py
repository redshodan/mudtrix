from collections import AsyncIterable
from typing import Iterable, Awaitable, Iterator, Optional, Dict

from mautrix.bridge import BasePuppet
from mautrix.types import RoomID, UserID, ContentURI, SyncToken
from mautrix.util.simple_template import SimpleTemplate
from yarl import URL

from .config import Config

config: Config


class Puppet(BasePuppet):

    by_mudid: Dict[UserID, 'Puppet'] = {}
    by_custom_mxid: Dict[UserID, 'Puppet'] = {}
    mxid_template: SimpleTemplate[int]

    def __init__(self, mudid=None, baseUrl=None, accessToken=None):
        print(f"Puppet({mudid}")
        self.access_token = accessToken
        self.base_url = URL(baseUrl) if baseUrl else None
        self.mudid = mudid
        print(f"Puppet mudid={mudid:} got={self.get_mxid_from_id(mudid)}")
        print(f"MUDPuppet {id(self)}")
        self.custom_mxid = self.get_mxid_from_id(mudid)
        self.default_mxid = self.get_mxid_from_id(mudid)
        self.default_mxid_intent = self.az.intent.user(self.default_mxid)
        self.intent = self._fresh_intent()

    @classmethod
    async def get_by_mxid(cls, mxid: UserID, create: bool = True):
        gid = cls.get_id_from_mxid(mxid)
        if gid:
            return cls.get_by_gid(gid, create)

        return None

    @classmethod
    def get_id_from_mxid(cls, mxid: UserID) -> Optional[int]:
        return cls.mxid_template.parse(mxid)

    @classmethod
    def get_mxid_from_id(cls, mudId: int) -> UserID:
        return UserID(cls.mxid_template.format_full(mudId))

    # @classmethod
    # def get_id_from_mxid(cls, mxid: UserID):
    #     prefix = cls._mxid_prefix
    #     suffix = cls._mxid_suffix
    #     if mxid[:len(prefix)] == prefix and mxid[-len(suffix):] == suffix:
    #         return mxid[len(prefix):-len(suffix)]
    #     return None

    @classmethod
    async def get_by_custom_mxid(cls, mxid: UserID) -> Optional['Puppet']:
        try:
            return cls.by_custom_mxid[mxid]
        except KeyError:
            return None

    @classmethod
    def get_all_with_custom_mxid(cls) -> Iterator['Puppet']:
        global config
        for name in config["mud.server.users"]:
            user = config[f"mud.server.users.{name}"]
            puppet = Puppet(mudid=name, baseUrl=config["homeserver.address"])
            print(puppet)
            yield puppet

    async def save(self) -> None:
        pass


def init(context: 'Context') -> Iterable[Awaitable[None]]:
    global config
    print("Puppet.init({context})")
    Puppet.az, config, Puppet.loop = context.core
    Puppet.mx = context.mx
    Puppet.hs_domain = config["homeserver"]["domain"]
    Puppet.mxid_template = SimpleTemplate(config["bridge.username_template"], "userid",
                                          prefix="@", suffix=f":{Puppet.hs_domain}", type=int)

    return (puppet.start() for puppet in Puppet.get_all_with_custom_mxid())
