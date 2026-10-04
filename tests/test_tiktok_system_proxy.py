# path: tests/test_tiktok_system_proxy.py

import urllib.request

import pytest

from f2.apps.tiktok import crawler as tiktok_crawler_module
from f2.apps.tiktok.crawler import TiktokCrawler
from f2.utils.http.impersonate import environment_proxy

KWARGS = {"headers": {"User-Agent": "f2-test"}, "cookie": "a=b"}


@pytest.fixture
def system_proxy(monkeypatch):
    """系统设置中的代理（macOS、Windows 上 urllib 会读取，libcurl 不会）"""
    settings = {"proxies": {"https": "127.0.0.1:7890"}, "bypass": False}
    monkeypatch.setattr(urllib.request, "getproxies", lambda: settings["proxies"])
    monkeypatch.setattr(urllib.request, "proxy_bypass", lambda host: settings["bypass"])
    return settings


@pytest.fixture
def transports(monkeypatch):
    created = []

    def create(**kwargs):
        created.append(kwargs)
        return None

    monkeypatch.setattr(tiktok_crawler_module, "create_impersonate_transport", create)
    return created


async def make_client(proxies):
    crawler = TiktokCrawler(KWARGS | {"proxies": proxies})
    crawler.aclient  # 创建客户端时挂载模拟浏览器的传输层
    await crawler.close()


def test_environment_proxy(system_proxy):
    assert environment_proxy("https://www.tiktok.com/") == "http://127.0.0.1:7890"

    system_proxy["bypass"] = True
    assert environment_proxy("https://www.tiktok.com/") is None

    system_proxy["bypass"] = False
    system_proxy["proxies"] = {}
    assert environment_proxy("https://www.tiktok.com/") is None


async def test_impersonate_transport_uses_system_proxy(system_proxy, transports):
    # 此前只开系统代理时 TikTok 接口直连，其他请求都走代理
    await make_client({"http://": None, "https://": None})

    assert transports[0]["proxy"] == "http://127.0.0.1:7890"


async def test_configured_proxy_still_wins(system_proxy, transports):
    await make_client({"type": "socks5", "host": "127.0.0.1", "port": 1080})

    assert transports[0]["proxy"] == "socks5://127.0.0.1:1080"
