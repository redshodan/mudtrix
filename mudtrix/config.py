from mautrix.bridge.config import BaseBridgeConfig, ConfigUpdateHelper


class Config(BaseBridgeConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        super().do_update(helper)

        copy, copy_dict, base = helper

        copy("homeserver.asmux")

        copy("mud.server")

        copy("appservice.community_id")

        copy("metrics.enabled")
        copy("metrics.listen_port")

        copy("bridge.username_template")
        copy("bridge.displayname_template")
        copy("bridge.community_template")
        copy("bridge.command_prefix")

        copy("bridge.initial_chat_sync")
        copy("bridge.invite_own_puppet_to_pm")
        copy("bridge.sync_with_custom_puppets")
        copy("bridge.sync_direct_chat_list")
        copy("bridge.double_puppet_server_map")
        copy("bridge.double_puppet_allow_discovery")
        if "bridge.login_shared_secret" in self:
            base["bridge.login_shared_secret_map"] = {
                base["homeserver.domain"]: self["bridge.login_shared_secret"]
            }
        else:
            copy("bridge.login_shared_secret_map")
        copy("bridge.update_avatar_initial_sync")
        copy("bridge.encryption.allow")
        copy("bridge.encryption.default")
        copy("bridge.encryption.database")
        copy("bridge.encryption.key_sharing.allow")
        copy("bridge.encryption.key_sharing.require_cross_signing")
        copy("bridge.encryption.key_sharing.require_verification")
        copy("bridge.delivery_receipts")
        copy("bridge.backfill.invite_own_puppet")
        copy("bridge.backfill.initial_limit")
        copy("bridge.backfill.missed_limit")
        copy("bridge.backfill.disable_notifications")
        copy("bridge.resend_bridge_info")
        copy("bridge.reconnect.max_retries")
        copy("bridge.reconnect.retry_backoff_base")

        copy("bridge.web.auth.public")
        copy("bridge.web.auth.prefix")
        if self["bridge.web.auth.shared_secret"] == "generate":
            base["bridge.web.auth.shared_secret"] = self._new_token()
        else:
            copy("bridge.web.auth.shared_secret")

        copy_dict("bridge.permissions")
