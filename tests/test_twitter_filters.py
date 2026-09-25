# path: tests/test_twitter_filters.py

import pytest

from f2.apps.twitter.crawler import TwitterCrawler
from f2.apps.twitter.filter import (
    BookmarkTweetFilter,
    LikeTweetFilter,
    PostTweetFilter,
    TweetDetailFilter,
)
from f2.apps.twitter.utils import (
    best_mp4_url,
    extract_desc,
    format_file_name,
    sort_mp4_urls,
)

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


def tweet_result(tweet_id, text, screen_name, variants=None):
    legacy = {
        "id_str": tweet_id,
        "full_text": text,
        "created_at": "Wed Oct 10 20:19:24 +0000 2018",
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
