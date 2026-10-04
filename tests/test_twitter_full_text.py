# path: tests/test_twitter_full_text.py

import pytest

from f2.apps.twitter.filter import (
    BookmarkTweetFilter,
    PostTweetFilter,
    TweetDetailFilter,
)
from f2.apps.twitter.utils import tweet_full_text

CURSORS = [
    {"entryId": "cursor-top-1", "content": {"cursorType": "Top", "value": "TOP"}},
    {"entryId": "cursor-bottom-1", "content": {"cursorType": "Bottom", "value": "BOT"}},
]
LONG = "长推文" * 120  # 360 个字，超过 280


def tweet(tweet_id, text, **extra):
    legacy = {"id_str": tweet_id, "full_text": text, "entities": {}}
    legacy.update(extra.pop("legacy", {}))
    user = {"id": "u1", "legacy": {"screen_name": "alice", "name": "爱丽丝"}}
    return {
        "rest_id": tweet_id,
        "legacy": legacy,
        "core": {"user_results": {"result": user}},
        **extra,
    }


def entry(result):
    item = {"itemType": "TimelineTweet", "tweet_results": {"result": result}}
    return {"entryId": f"tweet-{result['rest_id']}", "content": {"itemContent": item}}


RECOMMEND = {
    "entryId": "who-to-follow-1",
    "content": {"entryType": "TimelineTimelineModule", "items": []},
}


def timeline(*entries):
    return {"timeline": {"instructions": [{"entries": list(entries) + CURSORS}]}}


@pytest.mark.parametrize(
    "filter_cls, wrap",
    [
        (PostTweetFilter, lambda t: {"data": {"user": {"result": {"timeline_v2": t}}}}),
        (BookmarkTweetFilter, lambda t: {"data": {"bookmark_timeline_v2": t}}),
    ],
)
def test_text_stays_with_its_tweet_after_a_module(filter_cls, wrap):
    # 此前跳过没有文案的条目，推荐关注模块之后的推文都拿到了下一条推文的文案
    data = wrap(
        timeline(entry(tweet("1", "第一条")), RECOMMEND, entry(tweet("2", "第二条")))
    )

    items = filter_cls(data)._to_list()

    assert [(i["tweet_id"], i["tweet_desc_raw"]) for i in items[:3]] == [
        ("1", "第一条"),
        (None, ""),
        ("2", "第二条"),
    ]


def long_tweet():
    return tweet(
        "3",
        LONG[:279] + " https://t.co/more",
        note_tweet={"note_tweet_results": {"result": {"text": LONG, "entity_set": {}}}},
    )


def test_long_tweet_keeps_the_full_text():
    # legacy.full_text 只有前 279 个字，完整内容在 note_tweet 中
    data = {
        "data": {"user": {"result": {"timeline_v2": timeline(entry(long_tweet()))}}}
    }

    item = PostTweetFilter(data)._to_list()[0]

    assert item["tweet_desc_raw"] == LONG
    # 文件名中的 {desc} 不变，已下载的文件不会被重新下载
    assert item["tweet_desc"] == LONG[:279]


def test_detail_long_tweet_keeps_the_full_text():
    instructions = [{"type": "TimelineAddEntries", "entries": [entry(long_tweet())]}]
    data = {
        "data": {
            "threaded_conversation_with_injections_v2": {"instructions": instructions}
        }
    }

    assert TweetDetailFilter(data, "3").tweet_desc_raw == LONG


def test_links_are_expanded_and_text_after_them_kept():
    # 此前只保留第一个链接之前的内容
    result = tweet(
        "4",
        "报名入口 https://t.co/apply 截止到周五 &amp; 名额有限 https://t.co/media",
        legacy={
            "entities": {
                "urls": [
                    {
                        "url": "https://t.co/apply",
                        "expanded_url": "https://nasa.gov/apply",
                    }
                ],
                "media": [{"url": "https://t.co/media"}],
            }
        },
    )

    assert (
        tweet_full_text(result)
        == "报名入口 https://nasa.gov/apply 截止到周五 & 名额有限"
    )


def test_retweet_uses_the_original_text():
    original = tweet(
        "5",
        LONG[:279] + " https://t.co/more",
        note_tweet={"note_tweet_results": {"result": {"text": LONG}}},
    )
    original["core"]["user_results"]["result"]["legacy"]["screen_name"] = "NASASpox"
    result = tweet(
        "6",
        "RT @NASASpox: " + LONG[:120] + "…",
        legacy={"retweeted_status_result": {"result": original}},
    )

    assert tweet_full_text(result) == "RT @NASASpox: " + LONG


def test_not_a_tweet():
    assert tweet_full_text(None) == ""
    assert tweet_full_text({}) == ""
