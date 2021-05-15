from mautrix.bridge import BasePortal

from .config import Config
from .mud import MudClient


config: Config


class Portal(BasePortal):
    def __init__(self, *args, **kwargs):
        print(f"Portal(*args={args}, **kwargs={kwargs})")


def init(context) -> None:
    print(f"Portal.init({dir(context.config)})")
    print(f"{context.config.get('mud.server', 'default')}")
