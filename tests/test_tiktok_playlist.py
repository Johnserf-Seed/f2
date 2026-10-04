# path: tests/test_tiktok_playlist.py

import types

import pytest

from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok.filter import UserPlayListFilter

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.tiktok.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
    "url": "https://www.tiktok.com/@someone",
}
MIX_ID = "7122835631440857862"


def playlist_page(ids, has_more, cursor):
    # 实测（2026-10）：接口按 count 分页，cursor 是字符串形式的偏移量，最后一页 hasMore 为假
    return {
        "statusCode": 0,
        "playList": [{"mixId": i, "mixName": f"合集{i}", "videoCount": 3} for i in ids],
        "hasMore": has_more,
        "cursor": cursor,
    }


class PlayListCrawler:
    pages: list = []
    calls: list = []

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def fetch_user_play_list(self, params):
        type(self).calls.append(params)
        return type(self).pages.pop(0)  # 多请求一次就会因为没有页面而失败


@pytest.fixture
def handler(monkeypatch):
    # 请求参数模型换成普通对象，测试不依赖签名与令牌
    monkeypatch.setattr(tiktok_handler, "UserPlayList", types.SimpleNamespace)
    return tiktok_handler.TiktokHandler(dict(KWARGS))


def use_pages(monkeypatch, pages):
    crawler = type("Crawler", (PlayListCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(tiktok_handler, "TiktokCrawler", crawler)
    return crawler


def test_single_playlist_fields_are_lists():
    # 此前只有一个合集时 mixId 是字符串，选择列表会把 19 位 ID 的每个字符当成一个合集
    playlist = UserPlayListFilter(playlist_page([MIX_ID], False, "1"))

    assert playlist.mixId == [MIX_ID]
    assert playlist.mixName == [f"合集{MIX_ID}"]
    assert playlist.videoCount == [3]


async def test_fetch_play_list_reads_every_page(handler, monkeypatch):
    # TikTok 的 page_counts 默认是 5，此前只取第一页，合集多的用户只能看到前 5 个
    crawler = use_pages(
        monkeypatch,
        [playlist_page(["1"], True, "1"), playlist_page(["2"], False, "2")],
    )

    playlist = await handler.fetch_play_list("sec-uid", 0, 1)

    assert playlist.mixId == ["1", "2"]
    assert [params.cursor for params in crawler.calls] == [0, 1]


async def test_select_the_only_playlist(handler, monkeypatch):
    monkeypatch.setattr(
        tiktok_handler, "rich_prompt", types.SimpleNamespace(ask=lambda **kwargs: "1")
    )

    selected = await handler.select_playlist(
        UserPlayListFilter(playlist_page([MIX_ID], False, "1"))
    )

    assert selected == MIX_ID


async def test_no_playlist_ends_without_creating_the_user_folder(
    handler, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)  # 万一打开用户数据库，也只写到临时目录
    use_pages(monkeypatch, [playlist_page([], False, "0")])

    async def get_secuid(url, proxies=None):
        return "sec-uid"

    async def forbid(*args, **kwargs):
        raise AssertionError("没有合集时不应创建用户目录")

    monkeypatch.setattr(tiktok_handler.SecUserIdFetcher, "get_secuid", get_secuid)
    monkeypatch.setattr(handler, "get_or_add_user_data", forbid)

    await handler.handle_user_mix()
