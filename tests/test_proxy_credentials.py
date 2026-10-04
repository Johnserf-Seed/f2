# path: tests/test_proxy_credentials.py

import base64

import httpx
import pytest
from python_socks import parse_proxy_url

import f2.crawlers.websocket_crawler as websocket_crawler
from f2.crawlers.base_crawler import BaseCrawler
from f2.crawlers.websocket_crawler import WebSocketCrawler
from f2.utils.http.proxy import (
    ProxyConfig,
    ProxyType,
    check_proxy_avail,
    proxy_url_from_config,
)

try:  # websockets 16 起在 websockets.proxy 中
    from websockets.proxy import parse_proxy
except ImportError:
    from websockets.uri import parse_proxy

USER, PASSWORD = "us@er", "p@ss:w/rd#?%!"
URL = httpx.URL("https://x.com/i/api/graphql/abc/UserTweets")


def config(proxy_type="socks5", username=USER, password=PASSWORD):
    return {
        "type": proxy_type,
        "host": "127.0.0.1",
        "port": 1080,
        "username": username,
        "password": password,
    }


# ---------------- 配置文件中的用户名与密码 ----------------


@pytest.mark.parametrize(
    "username, password, expected",
    [
        (USER, PASSWORD, (USER, PASSWORD)),
        ("用户", "密 码", ("用户", "密 码")),
        # 此前只能自己按 URL 编码后填写，这样的配置仍然可用
        ("user", "p%40ss%2Fw", ("user", "p@ss/w")),
    ],
)
def test_config_credentials_are_kept(username, password, expected):
    # 此前直接拼进代理地址，httpx 与 python-socks 报端口无效，代理连接直接失败
    url = proxy_url_from_config(config("socks5", username, password))

    assert httpx.Proxy(url).auth == expected
    assert parse_proxy_url(url)[3:] == expected


def test_proxy_config_url_keeps_the_credentials():
    url = ProxyConfig(
        type=ProxyType.HTTP,
        host="127.0.0.1",
        port=8080,
        username=USER,
        password=PASSWORD,
    ).get_url()

    assert httpx.Proxy(url).auth == (USER, PASSWORD)


async def test_crawler_sends_the_original_credentials():
    crawler = BaseCrawler({}, proxies=config("http"))

    pool = crawler.aclient._transport_for_url(URL)._pool
    token = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
    assert (b"Proxy-Authorization", f"Basic {token}".encode()) in pool._proxy_headers
    await crawler.close()


def test_check_proxy_avail_accepts_the_credentials(monkeypatch):
    def request(self, method, url, **kwargs):
        return httpx.Response(
            200, json={"origin": "1.2.3.4"}, request=httpx.Request(method, url)
        )

    monkeypatch.setattr(httpx.Client, "request", request)

    assert check_proxy_avail(config("http")) is True


# ---------------- 直播弹幕的 WebSocket 连接 ----------------


def test_websockets_receives_the_original_credentials():
    # websockets 17.2 之前的版本不解码，/、?、# 只有 17.2 起才能使用
    password = PASSWORD if websocket_crawler._DECODES_PROXY_AUTH else "p@ss:w!rd%"
    crawler = WebSocketCrawler(
        {}, proxy=proxy_url_from_config(config("http", password=password))
    )

    proxy = parse_proxy(crawler.proxy)
    assert (proxy.username, proxy.password) == (USER, password)


@pytest.mark.parametrize(
    "decodes, expected",
    [
        (True, "socks5://us%40er:p%40ss%21@127.0.0.1:1080"),
        (False, "socks5://us@er:p@ss!@127.0.0.1:1080"),
    ],
)
def test_websockets_proxy_follows_the_installed_version(monkeypatch, decodes, expected):
    monkeypatch.setattr(websocket_crawler, "_DECODES_PROXY_AUTH", decodes)
    url = proxy_url_from_config(config(password="p@ss!"))

    assert WebSocketCrawler({}, proxy=url).proxy == expected
    assert WebSocketCrawler({}, proxy="http://127.0.0.1:7890").proxy == (
        "http://127.0.0.1:7890"
    )
    assert WebSocketCrawler({}, proxy=None).proxy is None
