# path: tests/test_twitter_filters.py

import pytest

from f2.apps.twitter import handler as twitter_handler
from f2.apps.twitter.crawler import TwitterCrawler
from f2.apps.twitter.filter import (
    BookmarkTweetFilter,
    LikeTweetFilter,
    PostTweetFilter,
    TweetDetailFilter,
    UserProfileFilter,
)
from f2.apps.twitter.handler import TwitterHandler
from f2.apps.twitter.utils import (
    best_mp4_url,
    extract_desc,
    format_file_name,
    newest_tweet_timestamp,
    sort_mp4_urls,
    tweet_created_at_to_timestamp,
)
from f2.utils.time.filter import filter_by_date_interval
from f2.utils.time.timestamp import parse_interval

# 接口返回的变体顺序不固定，m3u8 是播放列表而不是视频文件
VARIANTS = [
    {"bitrate": 2176000, "content_type": "video/mp4", "url": "https://v/720.mp4"},
    {"bitrate": 632000, "content_type": "video/mp4", "url": "https://v/320.mp4"},
    {"bitrate": 10368000, "content_type": "video/mp4", "url": "https://v/1080.mp4"},
    {"content_type": "application/x-mpegURL", "url": "https://v/pl.m3u8"},
]
CURSORS = [
    {"entryId": "cursor-top-1", "content": {"cursorType": "Top", "value": "TOP"}},
    {"entryId": "cursor-bottom-1", "content": {"cursorType": "Bottom", "value": "BOT"}},
]


def tweet_result(tweet_id, text, screen_name, variants=None, created_at=None):
    legacy = {
        "id_str": tweet_id,
        "full_text": text,
        "created_at": created_at or "Wed Oct 10 20:19:24 +0000 2018",
    }
    if variants is not None:
        media = [{"type": "video", "video_info": {"variants": variants}}]
        legacy["entities"] = {"media": media}
        legacy["extended_entities"] = {"media": media}
    user = {"legacy": {"screen_name": screen_name, "name": screen_name}}
    return {"legacy": legacy, "core": {"user_results": {"result": user}}}


def entry(tweet_id, result):
    item = {"itemType": "TimelineTweet", "tweet_results": {"result": result}}
    return {"entryId": f"tweet-{tweet_id}", "content": {"itemContent": item}}


def detail(entries, clear_cache=True):
    instructions = [{"type": "TimelineClearCache"}] if clear_cache else []
    instructions.append({"type": "TimelineAddEntries", "entries": entries})
    return {
        "data": {
            "threaded_conversation_with_injections_v2": {"instructions": instructions}
        }
    }


# ---------------- 推文详情定位（#436、#404、#234） ----------------


def test_detail_skips_clear_cache_instruction():
    data = detail([entry("111", tweet_result("111", "主推文 https://t.co/x", "alice"))])
    tweet = TweetDetailFilter(data, "111")
    assert tweet.tweet_id == "111"
    assert tweet.tweet_desc == "主推文"
    assert tweet.user_unique_id == "alice"


def test_detail_picks_reply_instead_of_parent():
    data = detail(
        [
            entry("111", tweet_result("111", "主推文", "parent")),
            entry("222", tweet_result("222", "评论内容", "child")),
        ]
    )
    tweet = TweetDetailFilter(data, "222")
    assert tweet.tweet_id == "222"
    assert tweet.user_unique_id == "child"


def test_detail_unwraps_tweet_with_visibility_results():
    wrapped = {
        "__typename": "TweetWithVisibilityResults",
        "tweet": tweet_result("333", "受限推文", "hidden"),
    }
    tweet = TweetDetailFilter(detail([entry("333", wrapped)]), "333")
    assert tweet.tweet_id == "333"
    assert tweet.tweet_desc == "受限推文"


def test_detail_still_reads_old_structure_and_defaults_to_first_tweet():
    data = detail(
        [
            entry("444", tweet_result("444", "旧结构", "old")),
            entry("555", tweet_result("555", "第二条", "other")),
        ],
        clear_cache=False,
    )
    assert TweetDetailFilter(data, "444").tweet_id == "444"
    assert TweetDetailFilter(data).tweet_id == "444"


def test_extract_desc_handles_missing_text():
    assert extract_desc(None) == ""
    assert extract_desc("") == ""
    assert extract_desc("  你好 https://t.co/x ") == "你好"


# ---------------- 视频只取 MP4（#436、#368） ----------------


def test_sort_mp4_urls_orders_by_bitrate_and_drops_m3u8():
    assert sort_mp4_urls(VARIANTS) == [
        "https://v/320.mp4",
        "https://v/720.mp4",
        "https://v/1080.mp4",
    ]
    assert sort_mp4_urls(VARIANTS[0]) == ["https://v/720.mp4"]
    assert sort_mp4_urls(None) == []
    assert best_mp4_url(VARIANTS) == "https://v/1080.mp4"
    assert best_mp4_url(VARIANTS[3:]) is None


def test_detail_video_url_ends_with_best_mp4():
    data = detail([entry("1", tweet_result("1", "视频", "alice", VARIANTS))])
    urls = TweetDetailFilter(data, "1").tweet_video_url
    # 下载器取列表最后一个，所以最后一个必须是最高码率
    assert urls[-1] == "https://v/1080.mp4"
    assert all(url.endswith(".mp4") for url in urls)


def post_timeline(tweets):
    entries = [
        entry(tid, tweet_result(tid, "t", screen, variants))
        for tid, screen, variants in tweets
    ]
    return {
        "data": {
            "user": {
                "result": {
                    "timeline_v2": {
                        "timeline": {"instructions": [{"entries": entries + CURSORS}]}
                    }
                }
            }
        }
    }


def test_post_video_url_picks_best_mp4_even_when_m3u8_is_last():
    videos = PostTweetFilter(post_timeline([("1", "alice", VARIANTS)])).tweet_video_url
    assert videos[0] == ["https://v/1080.mp4"]


# ---------------- ct0 自动作为 X-Csrf-Token（#426、#442） ----------------


@pytest.mark.parametrize(
    "extra, expected",
    [
        ({"cookie": "auth_token=a; ct0=fresh"}, "fresh"),
        ({"cookie": "ct0=fresh", "X-Csrf-Token": "stale"}, "fresh"),
        ({"cookie": "auth_token=a", "X-Csrf-Token": "configured"}, "configured"),
    ],
)
def test_csrf_token_prefers_ct0_from_cookie(extra, expected):
    crawler = TwitterCrawler({"headers": {"User-Agent": "f2-test"}} | extra)
    assert crawler.headers["X-Csrf-Token"] == expected


# ---------------- 主页、点赞、书签的 {uid} 命名（#442） ----------------


@pytest.mark.parametrize("filter_cls", [PostTweetFilter, LikeTweetFilter])
def test_timeline_uid_naming(filter_cls):
    item = filter_cls(post_timeline([("1", "alice", None)]))._to_list()[0]
    assert format_file_name("{uid}", item) == "alice"


def test_bookmark_uid_naming():
    entries = [entry("3", tweet_result("3", "t", "bob"))] + CURSORS
    data = {
        "data": {
            "bookmark_timeline_v2": {
                "timeline": {"instructions": [{"entries": entries}]}
            }
        }
    }
    item = BookmarkTweetFilter(data)._to_list()[0]
    assert format_file_name("{uid}", item) == "bob"


# ---------------- 主页 profile 的新结构（legacy 中已移除的字段） ----------------


def user_profile(**result_extra):
    result = {
        "rest_id": "123",
        "core": {"screen_name": "alice", "name": "Alice"},
        "pinned_items": {"tweet_ids_str": ["999"]},
        "action_counts": {"favorites_count": 42},
    }
    result.update(result_extra)
    return {"data": {"user": {"result": result}}}


def test_user_profile_reads_new_structure_fields():
    profile = UserProfileFilter(user_profile())
    assert profile.user_pined_tweet_id == "999"
    assert profile.favourites_count == 42


def test_user_profile_has_custom_timelines_returns_none():
    # 新结构已移除该字段，属性保留并返回 None
    assert UserProfileFilter(user_profile()).has_custom_timelines is None


def test_user_profile_missing_fields_do_not_raise():
    # 字段缺失时按缺失处理，不抛异常
    profile = UserProfileFilter({"data": {"user": {"result": {"rest_id": "123"}}}})
    assert profile.user_pined_tweet_id is None
    assert profile.favourites_count is None


# ---------------- 日期区间 --interval ----------------

# 2024-01-01 00:00:00（东八区），与 tests/test_parse_interval.py 的 START_2024 一致
START_2024 = 1704038400


def test_tweet_created_at_to_timestamp():
    assert tweet_created_at_to_timestamp("2024-01-01 00-00-00") == START_2024
    # 发布时间缺失时时间线过滤器给出的是 "Invalid timestamp"
    assert tweet_created_at_to_timestamp("Invalid timestamp") is None
    assert tweet_created_at_to_timestamp(None) is None
    assert tweet_created_at_to_timestamp("") is None


def test_newest_tweet_timestamp_ignores_older_pinned_tweet():
    # 置顶推文排在主页最前面、可能很久以前发布，取最新的一条才不会误判已翻过区间
    assert (
        newest_tweet_timestamp(["2019-01-01 00-00-00", "2024-01-01 00-00-00"])
        == START_2024
    )
    assert (
        newest_tweet_timestamp(["Invalid timestamp", "2024-01-01 00-00-00"])
        == START_2024
    )
    # 单条推文、以及一条都解析不出来时
    assert newest_tweet_timestamp("2024-01-01 00-00-00") == START_2024
    assert newest_tweet_timestamp([]) is None
    assert newest_tweet_timestamp(["Invalid timestamp"]) is None


async def test_interval_filter_matches_tweet_created_at_field():
    # 下载器按 "tweet_created_at" 筛选推文，字段名不一致会把整批推文都过滤掉
    items = PostTweetFilter(post_timeline([("1", "alice", None)]))._to_list()
    assert items[0]["tweet_created_at"] == "2018-10-10 20-19-24"

    kept = await filter_by_date_interval(
        items, "2018-01-01|2018-12-31", "tweet_created_at"
    )
    assert [item["tweet_created_at"] for item in kept] == ["2018-10-10 20-19-24"]

    # 区间外的推文、以及不带发布时间的光标条目都被过滤掉
    assert (
        await filter_by_date_interval(
            items, "2019-01-01|2019-12-31", "tweet_created_at"
        )
        == []
    )


def interval_page(tweets, cursor):
    """构造一页主页推文响应；只有一条推文加一个光标时，条目数为 2，触发翻完的结束条件"""
    entries = [
        entry(tweet_id, tweet_result(tweet_id, "t", "alice", created_at=created_at))
        for tweet_id, created_at in tweets
    ]
    entries.append(
        {
            "entryId": "cursor-bottom-1",
            "content": {"cursorType": "Bottom", "value": cursor},
        }
    )
    return {
        "data": {
            "user": {
                "result": {
                    "timeline_v2": {
                        "timeline": {"instructions": [{"entries": entries}]}
                    }
                }
            }
        }
    }


def interval_pages():
    return [
        # 第一页在区间内
        interval_page(
            [
                ("1", "Sat Jun 01 12:00:00 +0000 2024"),
                ("2", "Wed May 01 12:00:00 +0000 2024"),
            ],
            "cursor-1",
        ),
        # 第二页最新的一条早于区间开始时间
        interval_page(
            [
                ("3", "Fri Dec 01 12:00:00 +0000 2023"),
                ("4", "Wed Nov 01 12:00:00 +0000 2023"),
            ],
            "cursor-2",
        ),
        # 最后一页，接口给出 Bottom 光标，正常结束翻页
        interval_page([("5", "Wed Nov 01 12:00:00 +0000 2023")], "cursor-3"),
    ]


def post_handler(monkeypatch, pages):
    requested = []

    class DummyCrawler:
        def __init__(self, kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def fetch_post_tweet(self, params):
            requested.append(params.cursor)
            return pages[min(len(requested) - 1, len(pages) - 1)]

    monkeypatch.setattr(twitter_handler, "TwitterCrawler", DummyCrawler)

    handler = TwitterHandler(
        {
            "cookie": "a=b",
            "headers": {"User-Agent": "f2-test"},
            "proxies": {"http://": None, "https://": None},
            "timeout": 0,
        }
    )
    return handler, requested


async def test_post_stops_paging_when_page_is_before_interval_start(monkeypatch):
    handler, requested = post_handler(monkeypatch, interval_pages())

    pages_yielded = 0
    async for _ in handler.fetch_post_tweet(
        "u1", 20, "", None, parse_interval("2024-01-01|2024-12-31")
    ):
        pages_yielded += 1

    # 第二页仍有区间内的推文，这一页照常产出，但不再请求下一页
    assert len(requested) == 2
    assert requested == ["", "cursor-1"]
    assert pages_yielded == 2


async def test_post_keeps_paging_without_interval(monkeypatch):
    handler, requested = post_handler(monkeypatch, interval_pages())

    pages_yielded = 0
    async for _ in handler.fetch_post_tweet("u1", 20, "", None, None):
        pages_yielded += 1

    # 没有日期区间时一直翻到接口给出 Bottom 光标，这一页在产出前就结束
    assert len(requested) == 3
    assert pages_yielded == 2
