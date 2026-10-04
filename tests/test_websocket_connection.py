# path: tests/test_websocket_connection.py

import asyncio
import contextlib
import json
import socket
import urllib.request
from http import HTTPStatus

import pytest
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

import f2.apps.douyin.crawler as douyin_crawler_module
import f2.apps.tiktok.crawler as tiktok_crawler_module
import f2.crawlers.websocket_crawler as websocket_crawler_module
from f2.apps.douyin.crawler import DouyinWebSocketCrawler
from f2.apps.douyin.utils import TokenManager as DouyinTokenManager
from f2.apps.tiktok.crawler import TiktokWebSocketCrawler
from f2.crawlers.websocket_crawler import WebSocketCrawler
from f2.exceptions.api_exceptions import APIConnectionError

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.tiktok.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
}
CRAWLERS = [
    (douyin_crawler_module, DouyinWebSocketCrawler),
    (tiktok_crawler_module, TiktokWebSocketCrawler),
]


@pytest.fixture(autouse=True)
def no_proxy_or_network(monkeypatch):
    # 连接本机的测试服务器，不使用开发环境中的代理；抖音爬虫构造时会联网生成 ttwid
    monkeypatch.setattr(urllib.request, "getproxies", lambda: {})
    monkeypatch.setattr(
        DouyinTokenManager, "gen_ttwid", classmethod(lambda cls: "fake-ttwid")
    )


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def wait_for(condition, timeout=5):
    async def poll():
        while not condition():
            await asyncio.sleep(0.01)

    await asyncio.wait_for(poll(), timeout)


# ---------------- 客户端 ----------------


async def test_client_sends_headers_and_receives_messages():
    seen = {}

    async def handler(connection):
        seen["headers"] = connection.request.headers
        await connection.send(b"\x08\x01")
        await connection.close()

    received = []

    class Recorder(WebSocketCrawler):
        async def on_message(self, message):
            received.append(message)

    async with serve(handler, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        crawler = Recorder(wss_headers={"User-Agent": "f2-test", "Cookie": "a=b"})
        await crawler.connect_websocket(f"ws://127.0.0.1:{port}/webcast")

        assert await crawler.receive_messages() == "closed"

    assert received == [b"\x08\x01"]
    assert seen["headers"]["Cookie"] == "a=b"
    # 配置的 User-Agent 不会与 websockets 自带的重复
    assert seen["headers"].get_all("User-Agent") == ["f2-test"]


async def test_rejected_handshake_stops_retrying():
    # 此前服务器一直拒绝握手时会无限递归重试，程序不会结束
    attempts = []

    def reject(connection, request):
        attempts.append(request.path)
        return connection.respond(HTTPStatus.FORBIDDEN, "denied\n")

    async with serve(
        lambda connection: None, "127.0.0.1", 0, process_request=reject
    ) as server:
        port = server.sockets[0].getsockname()[1]
        crawler = WebSocketCrawler(wss_headers={})
        crawler.retry_delay = 0

        with pytest.raises(APIConnectionError):
            await crawler.connect_websocket(f"ws://127.0.0.1:{port}/webcast")

    assert len(attempts) == 3


@pytest.mark.parametrize("module, crawler_class", CRAWLERS)
@pytest.mark.parametrize(
    "proxies, expected",
    [
        # 没有配置代理时与其他请求一样使用环境变量与系统设置中的代理
        ({"http://": None, "https://": None}, True),
        ({"http://": "http://127.0.0.1:7890"}, "http://127.0.0.1:7890"),
        # 新格式的代理配置此前在弹幕连接中被忽略
        (
            {"type": "socks5", "host": "127.0.0.1", "port": 1080},
            "socks5://127.0.0.1:1080",
        ),
    ],
)
async def test_danmaku_connection_uses_configured_proxy(
    monkeypatch, module, crawler_class, proxies, expected
):
    captured = {}

    async def fake_connect(uri, **kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(websocket_crawler_module, "connect", fake_connect)
    crawler = crawler_class(KWARGS | {"proxies": proxies}, callbacks={})

    await crawler.connect_websocket("wss://example.invalid/webcast")

    assert captured["proxy"] == expected
    assert captured["additional_headers"]["User-Agent"] == "f2-test"


# ---------------- 本地转发服务器 ----------------


@pytest.mark.parametrize("module, crawler_class", CRAWLERS)
async def test_local_server_forwards_messages(monkeypatch, module, crawler_class):
    port = free_port()
    monkeypatch.setattr(
        module.ClientConfManager,
        "wss",
        classmethod(lambda cls: {"domain": "127.0.0.1", "port": port}),
    )
    crawler = crawler_class(KWARGS, callbacks={})
    crawler.timeout = 30
    server_task = asyncio.create_task(crawler.start_server())
    try:
        client = None
        for _ in range(100):  # 等待服务器开始监听
            with contextlib.suppress(OSError):
                client = await connect(f"ws://127.0.0.1:{port}", proxy=None)
                break
            await asyncio.sleep(0.02)
        assert client is not None
        await wait_for(lambda: len(crawler.connected_clients) == 1)

        await crawler.broadcast_message(
            {"method": "WebcastChatMessage", "content": "你好"}
        )
        assert json.loads(await client.recv()) == {
            "method": "WebcastChatMessage",
            "content": "你好",
        }

        # 客户端断开后不再保留，转发时也不会再发给它
        await client.close()
        await wait_for(lambda: not crawler.connected_clients)
    finally:
        server_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await server_task
