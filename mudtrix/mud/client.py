import asyncio
import logging
import re
import enum

#from mautrix.util.logging import TraceLogger



CONNECT_RX = re.compile(r".*connects you to an existing character\.")
LOGGED_IN_RX = re.compile(r"^--__--LOGGED_IN--__--$")
DEFAULT_NOSPOOF_RX = re.compile(r"^\[[^\]]\] (.*)$")
YOU_PAGED_RX = re.compile(r"^You paged (.*) with '")
# TODO: this needs to be in config, not hard coded.
FAZ_URL_RX = re.compile(r"^\[Fazool\(#8\),saypose\] Fazool says, \"http://bit.ly/.*")


class LINE(enum.Enum):
    SAY = 1
    POSE = 2
    PAGE = 3


# [name, rx, lineType, matchUser, matchDBNum, matchForcerUser, matchForcerDBNum,
#  matchBody]
LINE_MATCHES = \
[
    ["PERSON_SPEAKS_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\),saypose\] (.*) says, \"(.*)\"$"),
     LINE.SAY, 1, 2, None, None, 4],
    ["PERSON_POSES_APOSTROPHE_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\),saypose\] \w+('s .*)$"),
     LINE.POSE, 1, 2, None, None, 3],
    ["PERSON_POSES_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\),saypose\] (.*)$"),
     LINE.POSE, 1, 2, None, None, 3],
    ["PERSON_WHISPERS_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\)\] .* whispers \"(.*)\"$"),
     LINE.PAGE, 1, 2, None, None, 3],
    ["PERSON_PAGES_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\),page\] .* pages: (.*)$"),
     LINE.PAGE, 1, 2, None, None, 3],
    ["PERSON_PAGE_POSES_APOSTROPHE_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\),page\] From afar, \w+('s .*)$"),
     LINE.PAGE, 1, 2, None, None, 3],
    ["PERSON_PAGE_POSES_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\),page\] From afar, (.*)$"),
     LINE.PAGE, 1, 2, None, None, 3],
    ["PERSON_ACTION_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\)\] (.*)$"),
     LINE.POSE, 1, 2, None, None, 3],
    ["PERSON_FORCED_SPEAKS_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\)<-([\w ]?)\(#(\d+)\),saypose\] (.*) says, \"(.*)\"$"),
     LINE.SAY, 1, 2, 3, 4, 6],
    ["PERSON_FORCED_POSES_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\)<-([\w ]?)\(#(\d+)\),saypose\] (.*)$"),
     LINE.POSE, 1, 2, 3, 4, 5],
    ["PERSON_TRIGGERED_SPEAKS_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\)\{[\w ]+\}\] (.*) says, \"(.*)\"$"),
     LINE.SAY, 3, None, 1, 2, 4],
    ["PERSON_TRIGGERED_POSES_RX",
     re.compile(r"^\[([\w ]+)\(#(\d+)\)\{[\w ]+\}\] ([\w]+) (.*)$"),
     LINE.POSE, 3, None, 1, 2, 4]
]


class State(enum.Enum):
    CONNECTING = 1
    CONNECTED = 2
    LOGGED_IN = 3


class MudClient:
    def __init__(self, mxUser):
        self.log = logging.getLogger(f"mudtrix.Client({mxUser.name})")
        self.mxUser = mxUser
        self.user = mxUser.name
        self.password = mxUser.password
        self.host = mxUser.mudHost
        self.port = mxUser.mudPort
        self.reader = None
        self.writer = None
        self.state = State.CONNECTING

    async def connect(self):
        self.log.info(f"Connecting to {self.host}:{self.port}")
        self.reader, self.writer = await asyncio.open_connection(self.host,
                                                                 self.port)

    def isConnected(self):
        return self.state == State.CONNECTED

    def isLoggedIn(self):
        return self.state == State.LOGGED_IN

    def write(self, buf):
        ret = self.writer.write(buf.encode("latin1"))
        return ret

    def sendMatrixMessage(self, body, line, lineType, mudUser, mudDBnum,
                          forcerUser, forcerDBnum):
        self.log.debug(f"sendMatrixMessage: {lineType.name} {mudUser}/{mudDBnum} <- {forcerUser}/{forcerDBnum}: {body}")

    def proccessLine(self, line, rx_name, rx, lineType, matchUser, matchDBNum,
                     matchForcerUser, matchForcerDBNum, matchBody):
        match = rx.match(line)
        if not match:
            return False
        self.log.debug(f"{rx_name}: {match}")

        self.sendMatrixMessage(
            match.group(matchBody), line, lineType,
            match.group(matchUser) if matchUser else None,
            match.group(matchDBNum) if matchDBNum else None,
            match.group(matchForcerUser) if matchForcerUser else None,
            match.group(matchForcerDBNum) if matchForcerDBNum else None)

        return True

    async def login(self):
        while not self.reader.at_eof():
            line = await self.reader.readline()
            line = line.decode("latin1").strip()
            self.log.debug(f"Line from MUD: {line}")

            # State: CONNECTING
            if self.state == State.CONNECTING and CONNECT_RX.match(line):
                self.log.info("Logging in...")
                self.write(f"connect {self.user} {self.password}\n")
                self.state = State.CONNECTED
                self.sendPlayerSetup()
            # State: CONNECTED
            elif self.state == State.CONNECTED and LOGGED_IN_RX.match(line):
                self.log.info("Logged in.")
                self.state = State.LOGGED_IN
                await self.mxUser.onConnect()
                return True

    async def run(self):
        self.log.debug(f"MUDClient.run: {self}")

        if self.state != State.LOGGED_IN:
            self.log.error(f"Error: MUDClient.run called with {self.state=}")
            return

        while not self.reader.at_eof():
            line = await self.reader.readline()
            line = line.decode("latin1").strip()
            self.log.debug(f"Line from MUD: {line}")

            # Action: Filters
            if FAZ_URL_RX.match(line):
                self.log.debug("Skipping predefined filters")
            # Action: self say
            if line.startswith("You say, ") or YOU_PAGED_RX.match(line):
                self.log.debug("Skipping my own line")
            # Action: self pose
            # TODO: track username changes, keep a self.currentUser, rebuild
            # a regex for it for use here instead of starts with.
            if line.startswith(self.user + " "):
                self.log.debug("Skipping self pose")

            for entry in LINE_MATCHES:
                if self.proccessLine(line, *entry):
                    break

    def sendPlayerSetup(self):
        self.write("@set me=nospoof\n")
        self.write("@pemit me=--__--LOGGED_IN--__--\n")


if __name__ == "__main__":
    mc = MudClient("bobbit", "bobbit", "sundive.dyndns.org", 4202)

    async def run(self):
        await mc.connect()
        await mc.login()
        await mc.run()

    asyncio.run(run())
