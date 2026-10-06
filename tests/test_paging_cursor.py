# path: tests/test_paging_cursor.py

import logging
import types

import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.apps.tiktok import handler as tiktok_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.douyin.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}


class PagedCrawler:
    """按顺序返回预设页面的爬虫替身，多请求一次就会因为没有页面而失败"""

    pages: list = []
    calls: list = []

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def _next(self, params):
        type(self).calls.append(params)
        return type(self).pages.pop(0)

    fetch_user_post = _next
    fetch_user_like = _next
    fetch_user_music_collection = _next
    fetch_user_collection = _next
    fetch_user_collects_video = _next
    fetch_user_mix = _next
    fetch_post_search = _next


def page(ids, has_more, cursor):
    return {
        "status_code": 0,
        "aweme_list": [{"aweme_id": str(i)} for i in ids],
        "has_more": has_more,
        "max_cursor": cursor,
    }


# (生成器名, 调用参数)
GENERATORS = [
    ("fetch_user_post_videos", ("sec-uid", 0, 0, 20, None)),
    ("fetch_user_like_videos", ("sec-uid", 0, 20, None)),
    ("fetch_user_feed_videos", ("sec-uid", 0, 20, None)),
]


@pytest.fixture
def douyin(monkeypatch):
    # 请求参数模型构造时会联网获取 msToken，换成普通对象
    for name in (
        "UserPost",
        "UserLike",
        "UserMusicCollection",
        "UserCollection",
        "UserCollectsVideo",
        "UserMix",
    ):
        monkeypatch.setattr(douyin_handler, name, types.SimpleNamespace)
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    async def profile(*args, **kwargs):
        return types.SimpleNamespace(nickname_raw="作者")

    monkeypatch.setattr(handler, "fetch_user_profile", profile)
    return handler


def use_pages(monkeypatch, module, crawler_name, pages):
    crawler = type("Crawler", (PagedCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(module, crawler_name, crawler)
    return crawler


async def collect(generator):
    return [page.aweme_id async for page in generator]


def f2_warnings(caplog):
    return [
        r for r in caplog.records if r.name == "f2" and r.levelno == logging.WARNING
    ]


@pytest.mark.parametrize("name, args", GENERATORS, ids=[g[0] for g in GENERATORS])
async def test_stops_after_the_last_page(douyin, monkeypatch, name, args):
    # has_more 为假的最后一页之后不再请求（此前会拿着返回的游标再请求一次）
    crawler = use_pages(
        monkeypatch,
        douyin_handler,
        "DouyinCrawler",
        [page([1, 2], 1, 100), page([3], 0, 200)],
    )

    assert await collect(getattr(douyin, name)(*args)) == [["1", "2"], ["3"]]
    assert len(crawler.calls) == 2


@pytest.mark.parametrize("name, args", GENERATORS, ids=[g[0] for g in GENERATORS])
async def test_empty_page_moves_to_the_next_page(douyin, monkeypatch, name, args):
    crawler = use_pages(
        monkeypatch,
        douyin_handler,
        "DouyinCrawler",
        [page([], 1, 100), page([1], 0, 200)],
    )

    assert await collect(getattr(douyin, name)(*args)) == [[], ["1"]]
    assert [params.max_cursor for params in crawler.calls] == [0, 100]


@pytest.mark.parametrize(
    "first_page",
    [page([], 1, 0), page([1], 1, 0)],
    ids=["empty_page", "page_with_posts"],
)
@pytest.mark.parametrize("name, args", GENERATORS, ids=[g[0] for g in GENERATORS])
async def test_same_cursor_stops_paging(
    douyin, monkeypatch, caplog, name, args, first_page
):
    # 接口返回的游标与本次请求相同，再请求只会得到同一页；此前空页面会不间断地重复请求
    crawler = use_pages(monkeypatch, douyin_handler, "DouyinCrawler", [first_page])

    with caplog.at_level(logging.INFO):
        await collect(getattr(douyin, name)(*args))

    assert len(crawler.calls) == 1
    assert len(f2_warnings(caplog)) == 1


async def test_tiktok_search_stops_when_the_offset_does_not_move(monkeypatch, caplog):
    # 搜索接口出错时没有作品，cursor 也可能为空，此前会用同一个 offset 不间断地重复请求
    monkeypatch.setattr(tiktok_handler, "PostSearch", types.SimpleNamespace)
    handler = tiktok_handler.TiktokHandler(dict(KWARGS))

    crawler = use_pages(
        monkeypatch,
        tiktok_handler,
        "TiktokCrawler",
        [{"status_code": 10101, "item_list": [], "has_more": 1}],
    )

    with caplog.at_level(logging.INFO):
        pages = [
            search async for search in handler.fetch_search_videos("关键词", 0, 10)
        ]

    assert pages == []
    assert len(crawler.calls) == 1
    assert len(f2_warnings(caplog)) == 1


def cursor_page(key, ids, has_more, cursor):
    return {
        "status_code": 0,
        key: [{"aweme_id": str(i), "id": str(i)} for i in ids],
        "has_more": has_more,
        "cursor": cursor,
    }


# 用 cursor 字段翻页的列表：(生成器名, 调用参数, 条目列表所在的字段)
CURSOR_GENERATORS = [
    ("fetch_user_music_collection", (0, 20, None), "mc_list"),
    ("fetch_user_collection_videos", (0, 20, None), "aweme_list"),
    ("fetch_user_collects_videos", ("collects-id", 0, 20, None), "aweme_list"),
    ("fetch_user_mix_videos", ("mix-id", 0, 20, None), "aweme_list"),
]


@pytest.mark.parametrize(
    "name, args, key", CURSOR_GENERATORS, ids=[g[0] for g in CURSOR_GENERATORS]
)
async def test_cursor_lists_stop_when_the_cursor_does_not_move(
    douyin, monkeypatch, caplog, name, args, key
):
    crawler = use_pages(
        monkeypatch, douyin_handler, "DouyinCrawler", [cursor_page(key, [1], 1, 0)]
    )

    with caplog.at_level(logging.INFO):
        pages = [page async for page in getattr(douyin, name)(*args)]

    assert len(pages) == 1
    assert len(crawler.calls) == 1
    assert len(f2_warnings(caplog)) == 1


@pytest.mark.parametrize(
    "name, args, key", CURSOR_GENERATORS, ids=[g[0] for g in CURSOR_GENERATORS]
)
async def test_cursor_lists_follow_the_next_cursor(
    douyin, monkeypatch, caplog, name, args, key
):
    crawler = use_pages(
        monkeypatch,
        douyin_handler,
        "DouyinCrawler",
        [cursor_page(key, [1], 1, 100), cursor_page(key, [2], 0, 200)],
    )

    with caplog.at_level(logging.INFO):
        pages = [page async for page in getattr(douyin, name)(*args)]

    assert len(pages) == 2
    assert [params.cursor for params in crawler.calls] == [0, 100]
    assert f2_warnings(caplog) == []


# 主页作品与首页推荐都使用主页作品接口
POST_API_GENERATORS = [GENERATORS[0], GENERATORS[2]]


@pytest.mark.parametrize(
    "name, args", POST_API_GENERATORS, ids=[g[0] for g in POST_API_GENERATORS]
)
async def test_guest_cookie_page_without_paging_info_is_reported(
    douyin, monkeypatch, caplog, name, args
):
    # 实测（2026-10）：游客 cookie 请求第一页之后的页面只返回 {"status_code": 0}，
    # 没有作品也没有 has_more；此前提示“所有作品采集完毕”，像是已经下完了
    crawler = use_pages(
        monkeypatch,
        douyin_handler,
        "DouyinCrawler",
        [page([1, 2], 1, 100), {"status_code": 0}],
    )

    with caplog.at_level(logging.INFO):
        assert await collect(getattr(douyin, name)(*args)) == [["1", "2"], []]

    assert len(crawler.calls) == 2
    assert len(f2_warnings(caplog)) == 1


@pytest.mark.parametrize(
    "name, args", POST_API_GENERATORS, ids=[g[0] for g in POST_API_GENERATORS]
)
async def test_logged_in_end_of_list_is_not_a_warning(
    douyin, monkeypatch, caplog, name, args
):
    # 实测：登录状态下游标越过全部作品时返回空列表，但仍带有 has_more=0 与 max_cursor=0
    crawler = use_pages(
        monkeypatch,
        douyin_handler,
        "DouyinCrawler",
        [page([1], 1, 100), page([], 0, 0)],
    )

    with caplog.at_level(logging.INFO):
        assert await collect(getattr(douyin, name)(*args)) == [["1"], []]

    assert len(crawler.calls) == 2
    assert f2_warnings(caplog) == []
