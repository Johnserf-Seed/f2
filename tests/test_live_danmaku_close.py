# path: tests/test_live_danmaku_close.py

import asyncio
from types import SimpleNamespace

import pytest
from websockets.exceptions import ConnectionClosedOK
from websockets.frames import Close

import f2.apps.douyin.crawler as douyin_crawler_module
import f2.apps.tiktok.crawler as tiktok_crawler_module
from f2.apps.douyin import handler as douyin_handler
from f2.apps.douyin.crawler import DouyinWebSocketCrawler
from f2.apps.douyin.utils import TokenManager as DouyinTokenManager
from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok.crawler import TiktokWebSocketCrawler
from f2.crawlers.websocket_crawler import WebSocketCrawler

KWARGS = {
    "headers": {"User-Agent": "UA", "Referer": "https://www.tiktok.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
}


class FakeWebSocket:
    """recv 会一直等待到连接关闭；remote=True 表示服务器已经关闭了连接"""

    def __init__(self, remote=False):
        self.closed = remote
        self._closing = asyncio.Event()
        if remote:
            self._closing.set()

    async def recv(self):
        await self._closing.wait()
        raise ConnectionClosedOK(Close(1000, ""), Close(1000, ""))

    async def close(self):
        self.closed = True
        self._closing.set()


class FakeServer:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


# ---------------- WebSocketCrawler ----------------


async def test_receive_returns_the_reason_when_closed_by_crawler():
    crawler = WebSocketCrawler(wss_headers={}, timeout=5)
    crawler.websocket = FakeWebSocket()
    receiving = asyncio.create_task(crawler.receive_messages())
    await asyncio.sleep(0)

    await crawler.close_websocket(reason="no_client")
    assert await receiving == "no_client"


async def test_receive_reports_closed_when_server_closes():
    crawler = WebSocketCrawler(wss_headers={}, timeout=5)
    crawler.websocket = FakeWebSocket(remote=True)
    assert await crawler.receive_messages() == "closed"


# ---------------- 本地服务器 ----------------


@pytest.mark.parametrize(
    "crawler_class", [DouyinWebSocketCrawler, TiktokWebSocketCrawler]
)
async def test_timeout_check_closes_with_no_client_reason(crawler_class):
    crawler = crawler_class(KWARGS, callbacks={})
    crawler.timeout = 0.01
    crawler.websocket = FakeWebSocket()
    server = FakeServer()

    await crawler._timeout_check(server)
    assert server.closed and crawler.websocket.closed
    assert crawler.close_reason == "no_client"


@pytest.mark.parametrize(
    ("module", "crawler_class"),
    [
        (douyin_crawler_module, DouyinWebSocketCrawler),
        (tiktok_crawler_module, TiktokWebSocketCrawler),
    ],
)
async def test_busy_port_does_not_raise(monkeypatch, module, crawler_class):
    async def serve(*args, **kwargs):
        raise OSError(48, "Address already in use")

    monkeypatch.setattr(module, "serve", serve)
    errors = []
    monkeypatch.setattr(module.logger, "error", errors.append)

    # 启动失败只记录错误，不再抛出 UnboundLocalError 打断弹幕接收
    await crawler_class(KWARGS, callbacks={}).start_server()
    assert len(errors) == 1 and "Address already in use" in errors[0]


# ---------------- handler 的提示 ----------------


async def run_danmaku(monkeypatch, app, result):
    async def fetch_live_danmaku(self, params):
        return result

    infos = []
    callbacks = {"WebcastChatMessage": None}
    if app == "douyin":
        monkeypatch.setattr(DouyinTokenManager, "_msToken_cache", "tok")
        monkeypatch.setattr(
            douyin_handler,
            "DouyinWebcastSignature",
            lambda user_agent: SimpleNamespace(get_signature=lambda *args: "sig"),
        )
        monkeypatch.setattr(
            DouyinWebSocketCrawler, "fetch_live_danmaku", fetch_live_danmaku
        )
        monkeypatch.setattr(douyin_handler.logger, "info", infos.append)
        await douyin_handler.DouyinHandler(KWARGS).fetch_live_danmaku(
            room_id="1",
            user_unique_id="2",
            internal_ext="ext",
            cursor="c",
            wss_callbacks=callbacks,
        )
    else:
        monkeypatch.setattr(
            TiktokWebSocketCrawler, "fetch_live_danmaku", fetch_live_danmaku
        )
        monkeypatch.setattr(tiktok_handler.logger, "info", infos.append)
        await tiktok_handler.TiktokHandler(KWARGS).fetch_live_danmaku(
            room_id="1",
            internal_ext="ext",
            cursor="c",
            wrss="",
            wss_callbacks=callbacks,
        )
    return infos


@pytest.mark.parametrize("app", ["douyin", "tiktok"])
async def test_no_local_client_is_not_reported_as_live_ended(monkeypatch, app):
    infos = await run_danmaku(monkeypatch, app, "no_client")
    assert any("没有客户端连接" in message for message in infos)
    assert not any("已结束直播" in message for message in infos)


@pytest.mark.parametrize("app", ["douyin", "tiktok"])
async def test_closed_connection_does_not_claim_the_live_ended(monkeypatch, app):
    infos = await run_danmaku(monkeypatch, app, "closed")
    assert any("弹幕连接已关闭" in message for message in infos)
    assert not any("没有客户端连接" in message for message in infos)
