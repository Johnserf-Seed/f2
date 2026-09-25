# path: tests/test_handler_pagination.py

import types

import pytest

from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok.utils import normalize_cursor
from f2.apps.twitter import handler as twitter_handler
from f2.apps.weibo import handler as weibo_handler

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://example.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}


class FakeCrawler:
    """按顺序返回预设页面的爬虫替身，并记录每次请求的参数"""

    pages: list = []
    calls: list = []

    def __init__(self, kwargs=None):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def _next(self, params):
        type(self).calls.append(params)
        return type(self).pages.pop(0)  # 多请求一次就会因为没有页面而失败

    async def fetch_user_post(self, params):
        return self._next(params)

    async def fetch_user_like(self, params):
        return self._next(params)

    async def fetch_user_weibo(self, params):
        return self._next(params)

    async def fetch_post_tweet(self, params):
        return self._next(params)


def namespace(**fields):
    return types.SimpleNamespace(**fields)


def use_pages(monkeypatch, module, crawler_name, filter_name, param_names, pages):
    crawler = type("Crawler", (FakeCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(module, crawler_name, crawler)
    monkeypatch.setattr(module, filter_name, lambda response: namespace(**response))
    for name in param_names:  # 参数模型替换掉，TikTok 的模型在构造时会联网取 msToken
        monkeypatch.setattr(module, name, namespace)
    return crawler


def capture_bark(monkeypatch, handler):
    sent = []

    async def fake_send(title, body, *args, **kwargs):
        sent.append(body)

    monkeypatch.setattr(handler, "_send_bark_notification", fake_send)
    return sent


def tiktok_page(ids, has_more, cursor, nickname="作者", status=0):
    return dict(
        has_aweme=bool(ids),
        hasMore=has_more,
        cursor=cursor,
        aweme_id=ids,
        nickname_raw=[nickname] * len(ids),
        nickname=[nickname] * len(ids),
        desc=[""] * len(ids),
        api_status_code=status,
    )


async def collect(generator):
    return [page async for page in generator]


# ---------------- TikTok 游标（#270） ----------------


def test_normalize_cursor():
    assert normalize_cursor("1700000000000") == 1700000000000
    assert normalize_cursor(35) == 35
    assert normalize_cursor(None) is None
    assert normalize_cursor("abc", 0) == 0


async def test_tiktok_post_accepts_string_cursor_and_stops_after_last_page(
    monkeypatch,
):
    crawler = use_pages(
        monkeypatch,
        tiktok_handler,
        "TiktokCrawler",
        "UserPostFilter",
        ["UserPost"],
        [
            tiktok_page(["1", "2"], True, "1700000000000"),
            tiktok_page(["3"], False, "-1"),
        ],
    )
    handler = tiktok_handler.TiktokHandler(dict(KWARGS))
    sent = capture_bark(monkeypatch, handler)

    pages = await collect(handler.fetch_user_post_videos("sec-uid", 0, 0, 35, None))

    assert len(pages) == 2
    # 第二页用整数游标请求；最后一页之后不再请求，不会从头重新抓取
    assert crawler.calls[1].cursor == 1700000000000
    assert len(crawler.calls) == 2
    assert "作者" in sent[0]


async def test_tiktok_post_stops_on_empty_error_page(monkeypatch):
    # 空页面且 hasMore 为假时必须结束，即使接口返回了非 0 状态码
    use_pages(
        monkeypatch,
        tiktok_handler,
        "TiktokCrawler",
        "UserPostFilter",
        ["UserPost"],
        [tiktok_page([], False, "123", status=10201)],
    )
    handler = tiktok_handler.TiktokHandler(dict(KWARGS))
    sent = capture_bark(monkeypatch, handler)

    assert (
        await collect(handler.fetch_user_post_videos("sec-uid", 0, 0, 35, None)) == []
    )
    assert "sec-uid" in sent[0]  # 没有作品时用 secUid 作为昵称（#401）


async def test_tiktok_like_counts_each_page_once(monkeypatch):
    use_pages(
        monkeypatch,
        tiktok_handler,
        "TiktokCrawler",
        "UserPostFilter",
        ["UserLike"],
        [tiktok_page(["1", "2"], True, "10"), tiktok_page(["3", "4"], False, "0")],
    )
    handler = tiktok_handler.TiktokHandler(dict(KWARGS))
    capture_bark(monkeypatch, handler)
    monkeypatch.setattr(
        handler,
        "fetch_user_profile",
        lambda *a, **k: _async(namespace(nickname_raw="作者")),
    )

    pages = await collect(handler.fetch_user_like_videos("sec-uid", 0, 2, 4))

    # 上限是 4 个作品，两页各 2 个；以前每页计两次，只会下载第一页
    assert len(pages) == 2


async def _async(value):
    return value


# ---------------- 微博与 twitter 的默认昵称（#401） ----------------


@pytest.mark.parametrize(
    "page, expected",
    [
        (
            dict(
                weibo_id=["1"], since_id="", weibo_total=1, weibo_user_name_raw=["博主"]
            ),
            "博主",
        ),
        (
            dict(weibo_id=[], since_id="", weibo_total=0, weibo_user_name_raw=[]),
            "uid-1",
        ),
    ],
)
async def test_weibo_single_page_does_not_leave_nickname_unbound(
    monkeypatch, page, expected
):
    use_pages(
        monkeypatch,
        weibo_handler,
        "WeiboCrawler",
        "UserWeiboFilter",
        ["UserWeibo"],
        [page],
    )
    handler = weibo_handler.WeiboHandler(dict(KWARGS))
    sent = capture_bark(monkeypatch, handler)

    await collect(handler.fetch_user_weibo("uid-1"))

    assert expected in sent[0]


async def test_twitter_first_page_end_does_not_leave_nickname_unbound(monkeypatch):
    use_pages(
        monkeypatch,
        twitter_handler,
        "TwitterCrawler",
        "PostTweetFilter",
        ["PostTweetEncode"],
        [
            dict(
                cursorType="Bottom",
                entryId=["cursor-top", "cursor-bottom"],
                tweet_id=[],
                tweet_desc=[],
                nickname=[],
                nickname_raw=[],
                max_cursor="",
            )
        ],
    )
    handler = twitter_handler.TwitterHandler(dict(KWARGS))
    sent = capture_bark(monkeypatch, handler)

    assert await collect(handler.fetch_post_tweet("user-1")) == []
    assert "user-1" in sent[0]
