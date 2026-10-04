# path: tests/test_proxy_credentials.py

import base64

import click
import httpx
import pytest
from click.testing import CliRunner
from python_socks import parse_proxy_url

import f2.apps.bark.cli as bark_cli
import f2.apps.douyin.cli as douyin_cli
import f2.apps.tiktok.cli as tiktok_cli
import f2.apps.twitter.cli as twitter_cli
import f2.apps.weibo.cli as weibo_cli
import f2.crawlers.websocket_crawler as websocket_crawler
import f2.utils.http.proxy as proxy_module
from f2.crawlers.base_crawler import BaseCrawler
from f2.crawlers.websocket_crawler import WebSocketCrawler
from f2.utils.http.proxy import (
    ProxyConfig,
    ProxyType,
    check_proxy_avail,
    parse_proxy_address,
    proxy_url_from_config,
)

try:  # websockets 16 起在 websockets.proxy 中
    from websockets.proxy import parse_proxy
except ImportError:
    from websockets.uri import parse_proxy

USER, PASSWORD = "us@er", "p@ss:w/rd#?%!"
URL = httpx.URL("https://x.com/i/api/graphql/abc/UserTweets")
CLI_MODULES = [douyin_cli, tiktok_cli, twitter_cli, weibo_cli, bark_cli]


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


# ---------------- 命令行 --proxies ----------------


@pytest.mark.parametrize(
    "address, expected",
    [
        ("127.0.0.1:1080", {"host": "127.0.0.1", "port": 1080}),
        (
            "us@er:p@ss:w@127.0.0.1:1080",
            {"host": "127.0.0.1", "port": 1080, "username": USER, "password": "p@ss:w"},
        ),
        ("[::1]:1080", {"host": "[::1]", "port": 1080}),
    ],
)
def test_parse_proxy_address(address, expected):
    assert parse_proxy_address("socks5", address) == {"type": "socks5", **expected}


@pytest.mark.parametrize(
    "address", ["127.0.0.1", "127.0.0.1:", "127.0.0.1:port", ":1080", "h:0", "h:65536"]
)
def test_parse_proxy_address_rejects(address):
    with pytest.raises(ValueError):
        parse_proxy_address("socks5", address)


@pytest.fixture
def checked(monkeypatch):
    calls = []

    def check_proxy_avail(proxy_config, **kwargs):
        calls.append(proxy_config)
        return True

    for module in CLI_MODULES:
        monkeypatch.setattr(module, "check_proxy_avail", check_proxy_avail)
        monkeypatch.setattr(module, "get_f2_setting", lambda key, default=None: True)
    monkeypatch.setattr(proxy_module, "check_proxy_avail", check_proxy_avail)
    return calls


@pytest.mark.parametrize("module", CLI_MODULES, ids=lambda m: m.__name__.split(".")[2])
@pytest.mark.parametrize(
    "address, credentials",
    [("127.0.0.1:1080", None), ("us@er:p@ss@127.0.0.1:1080", (USER, "p@ss"))],
)
def test_cli_proxies_are_used(checked, module, address, credentials):
    # 此前 f2 x 的 socks5、https 代理被忽略；f2 bk 无法解析带用户名密码的地址
    ctx = click.Context(click.Command("f2"))
    proxies = module.validate_proxies(ctx, None, ("socks5", address))

    url = BaseCrawler({}, proxies=proxies)._get_proxy_config()
    assert parse_proxy_url(url)[1:3] == ("127.0.0.1", 1080)
    assert parse_proxy_url(url)[3:] == (credentials or ("", ""))


@pytest.mark.parametrize("module", CLI_MODULES, ids=lambda m: m.__name__.split(".")[2])
def test_cli_rejects_an_invalid_address(checked, module):
    ctx = click.Context(click.Command("f2"))
    with pytest.raises(click.BadParameter):
        module.validate_proxies(ctx, None, ("socks5", "127.0.0.1"))
    assert checked == []


def test_cli_proxy_is_checked_once(checked):
    CliRunner().invoke(douyin_cli.douyin, ["--proxies", "socks5", "127.0.0.1:1080"])

    assert checked == [{"type": "socks5", "host": "127.0.0.1", "port": 1080}]


def test_config_proxy_is_still_checked(checked, tmp_path):
    custom = tmp_path / "custom.yaml"
    custom.write_text(
        "douyin:\n  proxies:\n    type: socks5\n    host: 127.0.0.1\n    port: 1080\n",
        encoding="utf-8",
    )

    CliRunner().invoke(douyin_cli.douyin, ["-c", str(custom)])

    assert checked == [{"type": "socks5", "host": "127.0.0.1", "port": 1080}]
