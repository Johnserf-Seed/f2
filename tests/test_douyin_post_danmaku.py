# path: tests/test_douyin_post_danmaku.py

import asyncio
import types

import pytest

from f2.apps.douyin import handler as douyin_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}
TOTAL = 150
# 被过滤、不会返回的弹幕：一页常常不足请求的数量
HIDDEN = {i for i in range(TOTAL) if i % 3 == 0}


class DanmakuCrawler:
    """与实测一致的作品弹幕接口：按 offset 与 count 划出的窗口返回其中未被过滤的弹幕"""

    offsets: list = []
    hidden: set = HIDDEN
    # 为真时 has_more 一直为真，模拟接口不停给出空页面
    always_more = False

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_post_danmaku(self, params):
        type(self).offsets.append(params.offset)
        window = range(params.offset, min(params.offset + params.count, TOTAL))
        return {
            "status_code": 0,
            "danmaku_list": [
                {"danmaku_id": str(i), "text": f"弹幕 {i}"}
                for i in window
                if i not in type(self).hidden
            ],
            "end_time": params.offset + params.count,
            "total": TOTAL - len(type(self).hidden),
            "has_more": type(self).always_more or params.offset + params.count < TOTAL,
        }


@pytest.fixture
def handler(monkeypatch):
    # 请求参数模型构造时会联网获取 msToken，换成普通对象
    monkeypatch.setattr(douyin_handler, "PostDanmaku", types.SimpleNamespace)
    monkeypatch.setattr(douyin_handler, "DouyinCrawler", DanmakuCrawler)
    DanmakuCrawler.offsets = []
    DanmakuCrawler.hidden = HIDDEN
    DanmakuCrawler.always_more = False
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    async def no_bark(*args, **kwargs):
        return None

    monkeypatch.setattr(handler, "_send_bark_notification", no_bark)
    return handler


async def collect(handler):
    ids = []

    async def run():
        async for page in handler.fetch_post_danmaku("7000", 0, 50):
            ids.extend(page.danmaku_id or [])

    await asyncio.wait_for(run(), 5)
    return ids


async def test_post_danmaku_pages_cover_every_window_once(handler):
    # 此前 offset 加上的是累计数量（0、33、99…），第 3 页起跳过中间的弹幕，还会重复
    ids = await collect(handler)

    assert ids == [str(i) for i in range(TOTAL) if i not in HIDDEN]
    assert DanmakuCrawler.offsets == [0, 50, 100]


async def test_post_danmaku_stops_after_empty_pages(handler):
    # 窗口内的弹幕都被过滤、接口仍一直给出 has_more 时，连续 3 页为空即停止，
    # 不再无限请求
    DanmakuCrawler.hidden = set(range(TOTAL))
    DanmakuCrawler.always_more = True

    ids = await collect(handler)

    assert ids == []
    assert DanmakuCrawler.offsets == [0, 50, 100]
