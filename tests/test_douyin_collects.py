# path: tests/test_douyin_collects.py

import logging
import types

import pytest

from f2.apps.douyin import handler as douyin_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://example.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
    "url": "https://www.douyin.com/user/sec-uid",
    "page_counts": 5,
    "max_counts": 2,
}


class CollectsCrawler:
    """按顺序返回收藏夹列表各页的爬虫替身"""

    pages: list = []
    calls: list = []

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_user_collects(self, params):
        type(self).calls.append(params)
        return type(self).pages.pop(0)


class NoUserDB:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def folders_page(ids, has_more):
    return {
        "status_code": 0,
        "collects_list": [
            {"collects_id": i, "collects_name": f"收藏夹{i}", "total_number": 1}
            for i in ids
        ],
        "has_more": has_more,
        "cursor": max(ids, default=0),
    }


@pytest.fixture
def handler(monkeypatch, tmp_path):
    # 请求参数模型构造时会联网获取 msToken，用户数据库会写到当前目录，都换成替身
    monkeypatch.setattr(douyin_handler, "UserCollects", types.SimpleNamespace)
    monkeypatch.setattr(douyin_handler, "AsyncUserDB", NoUserDB)

    async def get_sec_user_id(url):
        return "sec-uid"

    monkeypatch.setattr(
        douyin_handler.SecUserIdFetcher, "get_sec_user_id", get_sec_user_id
    )

    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    async def get_or_add_user_data(*args):
        return tmp_path

    handler.selected = []
    handler.downloaded = []

    async def select_user_collects(collects):
        handler.selected.append(collects.collects_id)
        return collects.collects_id  # 选择“全部下载”

    async def fetch_user_collects_videos(collects_id, *args):
        handler.downloaded.append((collects_id, args))
        for _ in ():
            yield

    monkeypatch.setattr(handler, "get_or_add_user_data", get_or_add_user_data)
    monkeypatch.setattr(handler, "select_user_collects", select_user_collects)
    monkeypatch.setattr(
        handler, "fetch_user_collects_videos", fetch_user_collects_videos
    )
    return handler


def use_pages(monkeypatch, pages):
    crawler = type("Crawler", (CollectsCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(douyin_handler, "DouyinCrawler", crawler)
    return crawler


async def test_lists_every_folder_and_asks_once(handler, monkeypatch):
    # #443 复测：max_counts 为 2、page_counts 为 5 时只列出了第一页的 5 个收藏夹
    crawler = use_pages(
        monkeypatch,
        [folders_page([1, 2, 3, 4, 5], True), folders_page([6, 7, 8], False)],
    )

    await handler.handle_user_collects()

    assert len(crawler.calls) == 2
    assert handler.selected == [[1, 2, 3, 4, 5, 6, 7, 8]]
    assert [collects_id for collects_id, _ in handler.downloaded] == list(range(1, 9))
    # 作品数上限仍按每个收藏夹传给作品列表
    assert all(args == (0, 5, 2) for _, args in handler.downloaded)


async def test_no_folder_skips_the_prompt(handler, monkeypatch, caplog):
    use_pages(monkeypatch, [folders_page([], False)])

    with caplog.at_level(logging.INFO):
        await handler.handle_user_collects()

    assert handler.selected == []
    assert handler.downloaded == []
    warnings = [
        r for r in caplog.records if r.name == "f2" and r.levelno == logging.WARNING
    ]
    assert len(warnings) == 1
