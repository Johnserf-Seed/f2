# path: tests/test_douyin_max_counts.py

import types

import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.utils.json.filter import limit_page_items

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://example.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}

# 请求参数模型构造时会联网获取 msToken，测试里换成普通对象
PARAM_MODELS = [
    "UserPost",
    "UserLike",
    "UserMusicCollection",
    "UserCollection",
    "UserCollectsVideo",
    "UserMix",
    "PostRelated",
    "FriendFeed",
]


class WholePageCrawler:
    """不管请求的 count 是多少都返回整页的爬虫替身（#443 中喜欢、收藏接口的表现）"""

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
        return type(self).pages.pop(0)  # 多请求一次就会因为没有页面而失败

    fetch_user_post = _next
    fetch_user_like = _next
    fetch_user_music_collection = _next
    fetch_user_collection = _next
    fetch_user_collects_video = _next
    fetch_user_mix = _next
    fetch_post_related = _next
    fetch_friend_feed = _next


def aweme_page(count, cursor=1):
    return {
        "status_code": 0,
        "aweme_list": [{"aweme_id": str(i)} for i in range(count)],
        "has_more": 1,
        "max_cursor": cursor,
        "cursor": cursor,
    }


def music_page(count):
    return {
        "status_code": 0,
        "mc_list": [{"id": str(i)} for i in range(count)],
        "has_more": 1,
        "cursor": 1,
    }


def friend_page(count):
    return {
        "status_code": 0,
        "data": [{"aweme": {"aweme_id": str(i)}} for i in range(count)],
        "has_more": True,
        "cursor": 1,
        "level": 1,
    }


# (生成器名, 调用参数, 一页数据, 条目列表所在的字段, 统计条目的属性)
GENERATORS = [
    (
        "fetch_user_post_videos",
        ("sec-uid", 0, 0, 5, 2),
        aweme_page,
        "aweme_list",
        "aweme_id",
    ),
    (
        "fetch_user_like_videos",
        ("sec-uid", 0, 5, 2),
        aweme_page,
        "aweme_list",
        "aweme_id",
    ),
    ("fetch_user_music_collection", (0, 5, 2), music_page, "mc_list", "music_id"),
    ("fetch_user_collection_videos", (0, 5, 2), aweme_page, "aweme_list", "aweme_id"),
    (
        "fetch_user_collects_videos",
        ("collects-id", 0, 5, 2),
        aweme_page,
        "aweme_list",
        "aweme_id",
    ),
    (
        "fetch_user_mix_videos",
        ("mix-id", 0, 5, 2),
        aweme_page,
        "aweme_list",
        "aweme_id",
    ),
    (
        "fetch_user_feed_videos",
        ("sec-uid", 0, 5, 2),
        aweme_page,
        "aweme_list",
        "aweme_id",
    ),
    (
        "fetch_related_videos",
        ("aweme-id", "", 5, 2),
        aweme_page,
        "aweme_list",
        "aweme_id",
    ),
    ("fetch_friend_feed_videos", (0, 1, 0, 2), friend_page, "data", "aweme_id"),
]


@pytest.fixture
def handler(monkeypatch):
    for name in PARAM_MODELS:
        monkeypatch.setattr(douyin_handler, name, types.SimpleNamespace)
    handler = douyin_handler.DouyinHandler(dict(KWARGS))

    async def no_bark(*args, **kwargs):
        return None

    async def profile(*args, **kwargs):
        return types.SimpleNamespace(nickname_raw="作者")

    monkeypatch.setattr(handler, "_send_bark_notification", no_bark)
    monkeypatch.setattr(handler, "fetch_user_profile", profile)
    return handler


def use_pages(monkeypatch, pages):
    crawler = type("Crawler", (WholePageCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(douyin_handler, "DouyinCrawler", crawler)
    return crawler


def test_limit_page_items():
    page = {"aweme_list": [1, 2, 3], "has_more": 1}

    assert limit_page_items(page, "aweme_list", 2) == {
        "aweme_list": [1, 2],
        "has_more": 1,
    }
    assert page["aweme_list"] == [1, 2, 3]  # 不修改原来的数据
    assert limit_page_items(page, "aweme_list", 3) is page
    assert limit_page_items(page, "aweme_list", float("inf")) is page
    assert limit_page_items({"aweme_list": None}, "aweme_list", 1) == {
        "aweme_list": None
    }
    assert limit_page_items({}, "aweme_list", 1) == {}


@pytest.mark.parametrize(
    "name, args, make_page, key, field",
    GENERATORS,
    ids=[g[0] for g in GENERATORS],
)
async def test_whole_page_is_cut_to_max_counts(
    handler, monkeypatch, name, args, make_page, key, field
):
    # max_counts 为 2、每页请求 5 个，接口却返回整页 5 个：只交出 2 个，也不再请求下一页
    crawler = use_pages(monkeypatch, [make_page(5)])

    pages = [page async for page in getattr(handler, name)(*args)]

    assert [len(getattr(page, field)) for page in pages] == [2]
    assert len(pages[0]._to_raw()[key]) == 2
    assert len(crawler.calls) == 1


async def test_like_videos_keep_counting_across_pages(handler, monkeypatch):
    # 第一页不足上限时继续翻页，第二页只取剩下的数量
    crawler = use_pages(monkeypatch, [aweme_page(3), aweme_page(5, cursor=2)])

    pages = [page async for page in handler.fetch_user_like_videos("sec-uid", 0, 3, 4)]

    assert [len(page.aweme_id) for page in pages] == [3, 1]
    assert len(crawler.calls) == 2
