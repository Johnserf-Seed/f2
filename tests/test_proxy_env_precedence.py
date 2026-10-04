# path: tests/test_proxy_env_precedence.py

import httpx
import pytest
from httpx_socks import AsyncProxyTransport, SyncProxyTransport

from f2.crawlers.base_crawler import BaseCrawler

URL = httpx.URL("https://x.com/i/api/graphql/abc/UserTweets")
CONFIGURED = {"http://": "http://127.0.0.1:7890", "https://": "http://127.0.0.1:7890"}
SOCKS = {"type": "socks5", "host": "127.0.0.1", "port": 1080}
NONE = {"http://": None, "https://": None}


@pytest.fixture(autouse=True)
def environment_proxy(monkeypatch):
    """环境变量中的代理（macOS、Windows 上 httpx 还会读取系统设置中的代理）"""
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        monkeypatch.setenv(name, "http://10.9.9.9:1111")
    for name in ("NO_PROXY", "no_proxy", "ALL_PROXY", "all_proxy"):
        monkeypatch.delenv(name, raising=False)


def proxy_host(transport):
    proxy = getattr(getattr(transport, "_pool", None), "_proxy_url", None)
    return proxy.host.decode() if proxy else None


async def test_configured_proxy_wins_over_environment():
    # 此前环境与系统代理挂在 https:// 上，比配置的 all:// 更具体，配置的代理不生效
    crawler = BaseCrawler({}, proxies=CONFIGURED)

    assert proxy_host(crawler.aclient._transport_for_url(URL)) == "127.0.0.1"
    assert proxy_host(crawler.client._transport_for_url(URL)) == "127.0.0.1"
    await crawler.close()


async def test_configured_socks_proxy_wins_over_environment():
    crawler = BaseCrawler({}, proxies=SOCKS)

    assert isinstance(crawler.aclient._transport_for_url(URL), AsyncProxyTransport)
    assert isinstance(crawler.client._transport_for_url(URL), SyncProxyTransport)
    await crawler.close()


async def test_environment_proxy_is_used_without_configuration():
    # 没有在 F2 中配置代理时，仍然使用环境变量与系统设置中的代理
    crawler = BaseCrawler({}, proxies=NONE)

    assert proxy_host(crawler.aclient._transport_for_url(URL)) == "10.9.9.9"
    await crawler.close()
