import logging

from mautrix.bridge import Bridge
from mautrix.types import RoomID, UserID
from mautrix.util.logging import TraceLogger

from .config import Config
from .db import init as init_db
from .user import User, init as init_user
from .portal import Portal, init as init_portal
from .puppet import Puppet, init as init_puppet
from .matrix import MatrixHandler
from .context import Context
from .version import VERSION


class MUDBridge(Bridge):
    log: TraceLogger = logging.getLogger("mudtrix.Bridge")

    name = "mudtrix"
    module = "mudtrix"
    command = "python -m mudtrix"
    description = "A Matrix<->MUD puppeting bridge."
    repo_url = "https://github.com/redshodan/mudtrix"
    real_user_content_key = "mautrix.mud"
    version = VERSION
    config_class = Config
    matrix_class = MatrixHandler

    def prepare_db(self):
        super().prepare_db()
        init_db(self.db)
        self.log.info("prepare_db")

    def prepare_bridge(self):
        context = Context(az=self.az, config=self.config, loop=self.loop, bridge=self)
        self.matrix = context.mx = MatrixHandler(context)
        self.add_startup_actions(init_user(context))
        init_portal(context)
        self.add_startup_actions(init_puppet(context))
        if self.config["bridge.resend_bridge_info"]:
            self.add_startup_actions(self.resend_bridge_info())

    async def resend_bridge_info(self):
        self.config["bridge.resend_bridge_info"] = False
        self.config.save()
        self.log.info("Re-sending bridge info state event to all portals")
        for portal in Portal.all():
            await portal.update_bridge_info()
        self.log.info("Finished re-sending bridge info state events")

    def prepare_stop(self):
        self.log.debug("prepare_stop")
        for puppet in Puppet.by_custom_mxid.values():
            puppet.stop()

    def prepare_shutdown(self):
        self.log.debug("prepare_shutdown")

    async def get_portal(self, room_id: RoomID):
        return Portal.get_by_mxid(room_id)

    async def get_puppet(self, user_id: UserID, create: bool = False):
        return await Puppet.get_by_mxid(user_id, create=create)

    async def get_double_puppet(self, user_id: UserID):
        return await Puppet.get_by_custom_mxid(user_id)

    async def get_user(self, user_id: UserID):
        return User.get_by_mxid(user_id)

    def is_bridge_ghost(self, user_id: UserID):
        return bool(Puppet.get_id_from_mxid(user_id))

    async def count_logged_in_users(self) -> int:
        return len(User.by_mudUser)



MUDBridge().run()
