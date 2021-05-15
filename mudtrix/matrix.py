from mautrix.bridge import BaseMatrixHandler


class MatrixHandler(BaseMatrixHandler):
    def __init__(self, context) -> None:
        prefix, suffix = context.config["bridge.username_template"] \
                                .format(userid=":").split(":")
        homeserver = context.config["homeserver.domain"]
        self.user_id_prefix = f"@{prefix}"
        self.user_id_suffix = f"{suffix}:{homeserver}"

        super().__init__(bridge=context.bridge)
