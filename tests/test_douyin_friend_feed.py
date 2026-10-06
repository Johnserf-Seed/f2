# path: tests/test_douyin_friend_feed.py

import types

import pytest

from f2.apps.douyin import handler as douyin_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
    "cookie": "sessionid=login",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}


class FriendFeedCrawler:
    """按顺序返回好友作品各页的爬虫替身"""

    pages: list = []
    calls: list = []

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_friend_feed(self, params):
        type(self).calls.append(params)
        return type(self).pages.pop(0)  # 多请求一次就会因为没有页面而失败


def friend_page(ids, has_more, cursor, status_code=0):
    return {
        "status_code": status_code,
        "data": [{"aweme": {"aweme_id": str(i)}} for i in ids],
        "has_more": has_more,
        "cursor": cursor,
        "level": 1,
    }


@pytest.fixture
def handler(monkeypatch):
    # 请求参数模型构造时会联网获取 msToken，换成普通对象
    monkeypatch.setattr(douyin_handler, "FriendFeed", types.SimpleNamespace)
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    return handler


def use_pages(monkeypatch, pages):
    crawler = type("Crawler", (FriendFeedCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(douyin_handler, "DouyinCrawler", crawler)
    return crawler


async def collect(handler):
    return [page.aweme_id async for page in handler.fetch_friend_feed_videos()]


async def test_last_page_is_kept(handler, monkeypatch):
    # 最后一页的 has_more 为假，此前在交出作品之前就结束了，这一页不会下载
    crawler = use_pages(
        monkeypatch,
        [friend_page([1, 2], True, 100), friend_page([3], False, 200)],
    )

    assert await collect(handler) == [["1", "2"], ["3"]]
    assert [params.cursor for params in crawler.calls] == [0, 100]


async def test_empty_page_moves_to_the_next_page(handler, monkeypatch):
    crawler = use_pages(
        monkeypatch,
        [friend_page([], True, 100), friend_page([1], False, 200)],
    )

    assert await collect(handler) == [["1"]]
    assert [params.cursor for params in crawler.calls] == [0, 100]


async def test_empty_page_with_the_same_cursor_stops(handler, monkeypatch):
    # 此前空页面不更新游标，会用同一个游标不停地重复请求
    crawler = use_pages(monkeypatch, [friend_page([], True, 0)])

    assert await collect(handler) == []
    assert len(crawler.calls) == 1


async def test_error_status_stops(handler, monkeypatch):
    crawler = use_pages(monkeypatch, [friend_page([1], True, 100, status_code=8)])

    assert await collect(handler) == []
    assert len(crawler.calls) == 1
