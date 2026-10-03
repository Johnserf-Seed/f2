# path: tests/test_twitter_paging.py

import pytest

from f2.apps.twitter import handler as twitter_handler
from f2.utils.time.timestamp import parse_interval

KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://x.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
    "timeout": 0,
}
CURSORS = [
    {"entryId": "cursor-top-1", "content": {"cursorType": "Top", "value": "TOP"}},
    {"entryId": "cursor-bottom-1", "content": {"cursorType": "Bottom", "value": "BOT"}},
]
# 北京时间 2026-01-01 至 2026-01-31
INTERVAL = parse_interval("2026-01-01|2026-01-31")
NEWER = "Sun Mar 01 00:00:00 +0000 2026"
INSIDE = "Thu Jan 15 00:00:00 +0000 2026"
OLDER = "Mon Dec 01 00:00:00 +0000 2025"


def entry(tweet_id, created_at=INSIDE, pinned=False):
    item = {
        "itemType": "TimelineTweet",
        "tweet_results": {
            "result": {
                "rest_id": tweet_id,
                "legacy": {"id_str": tweet_id, "created_at": created_at},
                "core": {"user_results": {"result": {"id": "u1", "legacy": {}}}},
            }
        },
    }
    if pinned:
        item["socialContext"] = {"contextType": "Pin"}
    return {"entryId": f"tweet-{tweet_id}", "content": {"itemContent": item}}


def timeline(*entries):
    return {"timeline": {"instructions": [{"entries": list(entries) + CURSORS}]}}


def user_page(*entries):
    return {"data": {"user": {"result": {"timeline_v2": timeline(*entries)}}}}


def bookmark_page(*entries):
    return {"data": {"bookmark_timeline_v2": timeline(*entries)}}


class PagedCrawler:
    """按顺序返回预设页面的爬虫替身"""

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

    fetch_post_tweet = _next
    fetch_like_tweet = _next
    fetch_bookmark_tweet = _next


@pytest.fixture
def handler(monkeypatch):
    handler = twitter_handler.TwitterHandler(dict(KWARGS))

    async def no_bark(*args, **kwargs):
        return None

    monkeypatch.setattr(handler, "_send_bark_notification", no_bark)
    return handler


def use_pages(monkeypatch, pages):
    crawler = type("Crawler", (PagedCrawler,), {"pages": list(pages), "calls": []})
    monkeypatch.setattr(twitter_handler, "TwitterCrawler", crawler)
    return crawler


def tweet_ids(pages):
    return [[i["tweet_id"] for i in p._to_list() if i["tweet_id"]] for p in pages]


GENERATORS = [
    ("fetch_post_tweet", ("user-1", 20, ""), user_page),
    ("fetch_like_tweet", ("user-1", 20, ""), user_page),
    ("fetch_bookmark_tweet", (20, ""), bookmark_page),
]


@pytest.mark.parametrize(
    "name, args, make_page", GENERATORS, ids=[g[0] for g in GENERATORS]
)
async def test_whole_page_is_cut_to_max_counts(
    handler, monkeypatch, name, args, make_page
):
    # 接口不按 count 返回：max_counts 为 2 时一页 5 条只交出 2 条，也不再请求下一页
    crawler = use_pages(monkeypatch, [make_page(*(entry(str(i)) for i in range(5)))])

    pages = [page async for page in getattr(handler, name)(*args, 2)]

    assert tweet_ids(pages) == [["0", "1"]]
    assert len(crawler.calls) == 1


async def test_post_stops_after_reaching_interval_start(handler, monkeypatch):
    # 置顶推文早于区间不影响翻页；第二页最后一条早于区间开始，之后不再请求
    crawler = use_pages(
        monkeypatch,
        [
            user_page(
                entry("1", OLDER, pinned=True), entry("2", NEWER), entry("3", INSIDE)
            ),
            user_page(entry("4", INSIDE), entry("5", OLDER)),
        ],
    )

    pages = [
        page
        async for page in handler.fetch_post_tweet("user-1", 20, "", interval=INTERVAL)
    ]

    assert tweet_ids(pages) == [["3"], ["4"]]
    assert len(crawler.calls) == 2


async def test_like_pages_through_without_stopping_early(handler, monkeypatch):
    # 喜欢按点赞时间排列，较早发布的推文之后仍可能有区间内的推文
    crawler = use_pages(
        monkeypatch,
        [
            user_page(entry("1", OLDER)),
            user_page(entry("2", INSIDE), entry("3", NEWER)),
            user_page(),
        ],
    )

    pages = [
        page
        async for page in handler.fetch_like_tweet("user-1", 20, "", interval=INTERVAL)
    ]

    assert tweet_ids(pages) == [[], ["2"]]
    assert len(crawler.calls) == 3


async def test_max_counts_counts_tweets_inside_interval(handler, monkeypatch):
    # 设置日期区间时最大数量按区间内的推文计算，区间外的推文不占名额
    crawler = use_pages(
        monkeypatch,
        [
            user_page(entry("1", NEWER), entry("2", NEWER), entry("3", INSIDE)),
            user_page(entry("4", INSIDE), entry("5", INSIDE)),
        ],
    )

    pages = [
        page
        async for page in handler.fetch_post_tweet(
            "user-1", 20, "", 2, interval=INTERVAL
        )
    ]

    assert tweet_ids(pages) == [["3"], ["4"]]
    assert len(crawler.calls) == 2


async def test_tweet_repeated_on_next_page_is_kept_once(handler, monkeypatch):
    # 串推可能在相邻两页各出现一次，此前会重复计数并占用 --max-counts 的名额
    crawler = use_pages(
        monkeypatch,
        [
            user_page(entry("1"), entry("2")),
            user_page(entry("2"), entry("3")),
            user_page(),
        ],
    )

    pages = [page async for page in handler.fetch_post_tweet("user-1", 20, "", 3)]

    assert tweet_ids(pages) == [["1", "2"], ["3"]]
    assert len(crawler.calls) == 2
