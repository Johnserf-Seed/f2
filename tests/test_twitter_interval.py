# path: tests/test_twitter_interval.py

import pytest

from f2.apps.twitter.dl import TwitterDownloader
from f2.apps.twitter.filter import PostTweetFilter
from f2.apps.twitter.utils import tweet_created_at_to_timestamp

KWARGS = {
    "cookie": "a=b",
    "headers": {"User-Agent": "f2-test"},
    "proxies": {"http://": None, "https://": None},
}
CURSORS = [
    {"entryId": "cursor-top-1", "content": {"cursorType": "Top", "value": "TOP"}},
    {"entryId": "cursor-bottom-1", "content": {"cursorType": "Bottom", "value": "BOT"}},
]


def entry(tweet_id, created_at, pinned=False):
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


def page(*entries):
    timeline = {"instructions": [{"entries": list(entries) + CURSORS}]}
    return {"data": {"user": {"result": {"timeline_v2": {"timeline": timeline}}}}}


def test_tweet_created_at_to_timestamp():
    assert tweet_created_at_to_timestamp("Thu Jan 01 00:00:00 +0000 2026") == 1767225600
    assert tweet_created_at_to_timestamp(None) is None
    assert tweet_created_at_to_timestamp("2026-01-01") is None


def test_timeline_exposes_timestamps_and_pinned_marks():
    data = page(
        entry("9", "Wed Dec 31 17:00:00 +0000 2025", pinned=True),
        entry("10", "Thu Jan 01 15:30:00 +0000 2026"),
    )

    tweets = PostTweetFilter(data)

    assert tweets.tweet_timestamp == [1767200400, 1767281400, None, None]
    assert tweets.tweet_pinned == [True, False, False, False]


@pytest.fixture
def downloaded(monkeypatch):
    """记录交给下载处理的推文 ID，不真正下载"""
    ids = []

    async def handler_download(self, kwargs, tweet, user_path):
        ids.append(tweet.get("tweet_id"))

    async def execute_tasks(self):
        return None

    monkeypatch.setattr(TwitterDownloader, "handler_download", handler_download)
    monkeypatch.setattr(TwitterDownloader, "execute_tasks", execute_tasks)
    return ids


async def test_interval_uses_publish_time_in_beijing_time(downloaded, tmp_path):
    # 此前按不存在的 createTime 字段筛选，设置区间后一条推文都不下载（#461）；
    # 区间按北京时间计算，2026-01-01 是 UTC 2025-12-31 16:00 至 2026-01-01 15:59:59
    tweets = PostTweetFilter(
        page(
            entry("1", "Wed Dec 31 15:00:00 +0000 2025"),
            entry("2", "Wed Dec 31 17:00:00 +0000 2025"),
            entry("3", "Thu Jan 01 15:30:00 +0000 2026"),
            entry("4", "Thu Jan 01 16:30:00 +0000 2026"),
        )
    )._to_list()
    kwargs = KWARGS | {"interval": "2026-01-01|2026-01-01"}
    downloader = TwitterDownloader(kwargs)

    await downloader.create_download_tasks(kwargs, tweets, tmp_path)
    await downloader.close()

    assert downloaded == ["2", "3"]


async def test_interval_all_keeps_every_entry(downloaded, tmp_path):
    tweets = PostTweetFilter(
        page(entry("1", "Wed Dec 31 15:00:00 +0000 2025"))
    )._to_list()
    kwargs = KWARGS | {"interval": "all"}
    downloader = TwitterDownloader(kwargs)

    await downloader.create_download_tasks(kwargs, tweets, tmp_path)
    await downloader.close()

    # 游标条目也交给下载处理，在那里因为没有作者被跳过
    assert downloaded == ["1", None, None]
