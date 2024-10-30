# path: f2/apps/bark/utils.py

import f2

from f2.utils.conf_manager import ConfigManager


class ClientConfManager:
    """
    用于管理客户端配置 (Used to manage client configuration)
    """

    client_conf = ConfigManager(f2.F2_CONFIG_FILE_PATH).get_config("f2")
    bark_conf = client_conf.get("bark", {})

    @classmethod
    def client(cls) -> dict:
        return cls.bark_conf

    @classmethod
    def token(cls) -> str:
        return cls.client().get("token", "")

    @classmethod
    def proxies(cls) -> dict:
        return cls.client().get("proxies", {})

    @classmethod
    def encryption(cls) -> dict:
        return cls.client().get("encryption", {})
