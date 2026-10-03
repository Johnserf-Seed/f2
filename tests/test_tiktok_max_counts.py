# path: tests/test_tiktok_max_counts.py

import types

import pytest

from f2.apps.tiktok import handler as tiktok_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://www.tiktok.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}

# 请求参数模型换成普通对象，测试不依赖签名与令牌
PARAM_MODELS = ["UserPost", "UserLike", "UserCollect", "UserMix", "PostSearch"]


class WholePageCrawler:
    """不管请求的 count 是多少都返回整页的爬虫替身"""

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
    fetch_user_collect = _next
    fetch_user_mix = _next
    fetch_post_search = _next


def item_page(count):
    return {
        "statusCode": 0,
        "itemList": [{"id": str(i)} for i in range(count)],
        "hasMore": True,
        "cursor": "100",
    }


def search_page(count):
    return {
        "status_code": 0,
        "item_list": [{"id": str(i)} for i in range(count)],
        "has_more": 1,
        "cursor": 30,
        "extra": {"logid": "search-id"},
    }


# (生成器名, 调用参数, 一页数据, 条目列表所在的字段)
GENERATORS = [
    ("fetch_user_post_videos", ("sec-uid", 0, 0, 30, 2), item_page, "itemList"),
    ("fetch_user_like_videos", ("sec-uid", 0, 30, 2), item_page, "itemList"),
    ("fetch_user_collect_videos", ("sec-uid", 0, 30, 2), item_page, "itemList"),
    ("fetch_user_mix_videos", ("mix-id", 0, 30, 2), item_page, "itemList"),
    ("fetch_search_videos", ("keyword", 0, 30, 2), search_page, "item_list"),
]


@pytest.fixture
def handler(monkeypatch):
    for name in PARAM_MODELS:
        monkeypatch.setattr(tiktok_handler, name, types.SimpleNamespace)
    handler = tiktok_handler.TiktokHandler(dict(KWARGS))

    async def no_bark(*args, **kwargs):
        return None

    async def profile(*args, **kwargs):
        return types.SimpleNamespace(nickname_raw="作者")

    monkeypatch.setattr(handler, "_send_bark_notification", no_bark)
    monkeypatch.setattr(handler, "fetch_user_profile", profile)
    return handler


def use_pages(monkeypatch, pages):
    crawler = type("Crawler", (WholePageCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(tiktok_handler, "TiktokCrawler", crawler)
    return crawler


@pytest.mark.parametrize(
    "name, args, make_page, key",
    GENERATORS,
    ids=[g[0] for g in GENERATORS],
)
async def test_whole_page_is_cut_to_max_counts(
    handler, monkeypatch, name, args, make_page, key
):
    # max_counts 为 2，接口返回整页 30 个：只交出 2 个，也不再请求下一页
    crawler = use_pages(monkeypatch, [make_page(30)])

    pages = [page async for page in getattr(handler, name)(*args)]

    assert [len(page.aweme_id) for page in pages] == [2]
    assert len(pages[0]._to_raw()[key]) == 2
    assert len(crawler.calls) == 1
