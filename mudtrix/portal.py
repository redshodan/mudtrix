from typing import Dict, Any, Optional, Iterator

from mautrix.appservice import AppService
from mautrix.bridge import BasePortal
from mautrix.types import RoomID, SerializableEnum

from .config import Config


config: Config

class ConverastionType(SerializableEnum):
    MAIN = "main"
    PAGE = "page"


class Portal(BasePortal):
    by_mxid: Dict[RoomID, 'Portal'] = {}
    by_mudid: Dict[str, 'Portal'] = {}
    config: Config
    matrix: 'm.MatrixHandler'
    az: AppService

    def __init__(self, mudid: str, conv_type: ConverastionType):
        print(f"Portal({mudid=}, {conv_type=})")

    @property
    def bridge_info_state_key(self) -> str:
        return f"redshodan://mudtrix/{self.gid}"

    @property
    def bridge_info(self) -> Dict[str, Any]:
        return {
        "bridgebot": self.az.bot_mxid,
        "creator": self.main_intent.mxid,
        "protocol": {
             "id": "mudtrix",
             "displayname": "Mudtrix",
             "avatar_url": config["appservice.bot_avatar"]},
        "channel": {
             "id": self.gid,
             "displayname": self.name}
        }

    @classmethod
    def get_by_mxid(cls, mxid: RoomID) -> Optional['Portal']:
        cls.log.info("Portal.get_by_mxid")
        return None

    @classmethod
    def get_by_gid(cls, gid: str, receiver: Optional[str] = None, conv_type: Optional[int] = None,
                   ) -> Optional['Portal']:
        cls.log.info("Portal.get_by_gid")
        return None

    @classmethod
    def get_all_by_receiver(cls, receiver: str) -> Iterator['Portal']:
        cls.log.info("Portal.get_all_by_receiver")

    @classmethod
    def all(cls) -> Iterator['Portal']:
        cls.log.info("Portal.all")



def init(context) -> None:
    global config
    Portal.az, config, Portal.loop = context.core
    Portal.bridge = context.bridge
    Portal.matrix = context.mx
    Portal.invite_own_puppet_to_pm = config["bridge.invite_own_puppet_to_pm"]
