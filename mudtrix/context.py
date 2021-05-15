from typing import Tuple


class Context:
    def __init__(self, az, config, loop, bridge):
        self.az = az
        self.config = config
        self.loop = loop
        self.bridge = bridge
        self.mx = None

    @property
    def core(self) -> Tuple:
        return self.az, self.config, self.loop
