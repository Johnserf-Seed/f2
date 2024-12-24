# path: f2/apps/bark/utils.py

import f2
import secrets

from f2.utils.conf_manager import ConfigManager
from f2.utils.utils import merge_config


class ClientConfManager:
    """
    用于管理客户端配置 (Used to manage client configuration)
    """

    client_conf = ConfigManager(f2.F2_CONFIG_FILE_PATH).get_config("f2")
    app_conf = ConfigManager(f2.APP_CONFIG_FILE_PATH).get_config("bark")
    bark_conf = client_conf.get("bark", {})

    @classmethod
    def enable_bark(cls) -> bool:
        return cls.client_conf.get("enable_bark", False)

    @classmethod
    def client(cls) -> dict:
        return cls.bark_conf

    @classmethod
    def app(cls) -> dict:
        return cls.app_conf

    @classmethod
    def merge(cls) -> dict:
        return merge_config(cls.client(), cls.app())

    @classmethod
    def conf_version(cls) -> str:
        return cls.client_conf.get("version", "unknown")

    @classmethod
    def key(cls) -> str:
        return cls.app().get("key", "")

    @classmethod
    def token(cls) -> str:
        return cls.app().get("token", "")

    @classmethod
    def proxies(cls) -> dict:
        return cls.client().get("proxies", {})

    @classmethod
    def encryption(cls) -> dict:
        return cls.client().get("encryption", {})

    @classmethod
    def enable_encryption(cls) -> bool:
        return cls.encryption().get("enable", False)

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
