from typing import Awaitable, Dict, List
import asyncio
import logging

from mautrix.types import UserID, RoomID
from mautrix.util.logging import TraceLogger
from mautrix.bridge import BaseUser, BridgeState, async_getter_lock
from mautrix.util.bridge_state import BridgeStateEvent

from .config import Config
from .mud import MudClient


config: Config


class User(BaseUser):
    log: TraceLogger = logging.getLogger("mudtrix.User")

    by_mudUser: Dict[str, 'User'] = {}

    def __init__(self, name, password, dbnum):
        self.log.debug(f"User({name}, {password}, {dbnum})")
        self.mxid = UserID(f"@mud_{name}:{config['homeserver.domain']}")
        super().__init__()
        self.name = name
        self.password = password
        self.dbnum = dbnum

        serverCfg = config.get("mud.server", None)
        self.mudName = serverCfg.get("name")
        self.mudHost = serverCfg.get("host")
        self.mudPort = serverCfg.get("port")

        self.client = None

    async def login(self):
        self.log.debug(f"User.login: {self}")
        self.client = MudClient(self)
        await self.client.connect()
        await self.client.login()

    async def run(self):
        self.log.debug(f"User.run: {self}")
        await self.client.run()

    async def is_logged_in(self) -> bool:
        return self.client.isLoggedIn() if self.client else False

    async def get_direct_chats(self) -> Dict[UserID, List[RoomID]]:
        pass

    async def onConnect(self):
        self.log.info(f"onConnect({self.name})")
        User.by_mudUser[self.name] = self
        await self.push_bridge_state(BridgeStateEvent.CONNECTED)

    @classmethod
    async def init_all(cls):
        # cls.log.debug("User.init_all")
        # return []
        users = [user for user in cls.get_all()]
        cls.log.debug(f"{cls.loop=}")

        await asyncio.gather(*[user.login() for user in users])

        tasks = []
        for user in users:
            if await user.is_logged_in():
                tasks.append(asyncio.create_task(user.run()))
        return tasks

    @classmethod
    def get_all(cls):
        for name, user in config.get("mud.server.users", None).items():
            yield User(name, user.get("password"), user.get("dbnum"))


def init(context) -> Awaitable[None]:
    global config
    print(f"User.init({context})")
    User.az, config, User.loop = context.core
    User.bridge = context.bridge
    return User.init_all()
