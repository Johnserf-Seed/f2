# path: f2/apps/bark/utils.py

import f2
import secrets

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
    def key(cls) -> str:
        return cls.client().get("key", "")

    @classmethod
    def token(cls) -> str:
        return cls.client().get("token", "")

    @classmethod
    def proxies(cls) -> dict:
        return cls.client().get("proxies", {})

    @classmethod
    def encryption(cls) -> dict:
        return cls.client().get("encryption", {})

    @classmethod
    def headers(cls) -> dict:
        return cls.client().get("headers", {})

    @classmethod
    def user_agent(cls) -> str:
        return cls.headers().get("User-Agent", "")

    @classmethod
    def referer(cls) -> str:
        return cls.headers().get("Referer", "")


def generate_numeric_bytes(length: int) -> bytes:
    """生成由纯数字组成的字节"""
    numeric_str = "".join(secrets.choice("0123456789") for _ in range(length))
    return numeric_str.encode("utf-8")
