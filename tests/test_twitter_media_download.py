# path: tests/test_twitter_media_download.py

import pytest

from f2.apps.twitter.dl import TwitterDownloader
from f2.apps.twitter.filter import PostTweetFilter, TweetDetailFilter

KWARGS = {
    "cookie": "a=b",
    "headers": {"User-Agent": "f2-test"},
    "proxies": {"http://": None, "https://": None},
    "interval": "all",
    "naming": "{tweet_id}",
}
CURSORS = [
    {"entryId": "cursor-top-1", "content": {"cursorType": "Top", "value": "TOP"}},
    {"entryId": "cursor-bottom-1", "content": {"cursorType": "Bottom", "value": "BOT"}},
]


def photo(name):
    return {
        "type": "photo",
        "media_url_https": f"https://pbs.twimg.com/media/{name}.jpg",
    }


def video(name, media_type="video"):
    variants = [
        {"content_type": "application/x-mpegURL", "url": f"https://v/{name}.m3u8"},
        {
            "bitrate": 632000,
            "content_type": "video/mp4",
            "url": f"https://v/{name}-320.mp4",
        },
        {
            "bitrate": 2176000,
            "content_type": "video/mp4",
            "url": f"https://v/{name}-720.mp4",
        },
    ]
    return {
        "type": media_type,
        "media_url_https": f"https://pbs.twimg.com/thumb/{name}.jpg",
        "video_info": {"variants": variants},
    }


def tweet(tweet_id, *media):
    legacy = {
        "id_str": tweet_id,
        "full_text": "推文",
        "created_at": "Thu Jan 15 00:00:00 +0000 2026",
        "entities": {"media": list(media)},
        "extended_entities": {"media": list(media)},
    }
    user = {"id": "u1", "legacy": {"screen_name": "alice", "name": "爱丽丝"}}
    return {
        "rest_id": tweet_id,
        "legacy": legacy,
        "core": {"user_results": {"result": user}},
    }


def entry(result):
    tweet_id = result["rest_id"]
    item = {"itemType": "TimelineTweet", "tweet_results": {"result": result}}
    return {"entryId": f"tweet-{tweet_id}", "content": {"itemContent": item}}


def timeline(*results):
    entries = [entry(result) for result in results] + CURSORS
    instructions = [{"entries": entries}]
    return {
        "data": {
            "user": {
                "result": {"timeline_v2": {"timeline": {"instructions": instructions}}}
            }
        }
    }


@pytest.fixture
def downloads(monkeypatch):
    """记录交给下载的文件，不发出请求"""
    files = []

    async def initiate_download(self, file_type, url, base_path, name, suffix):
        files.append((name + suffix, url))

    async def initiate_static_download(self, *args, **kwargs):
        return None

    async def execute_tasks(self):
        return None

    monkeypatch.setattr(TwitterDownloader, "initiate_download", initiate_download)
    monkeypatch.setattr(
        TwitterDownloader, "initiate_static_download", initiate_static_download
    )
    monkeypatch.setattr(TwitterDownloader, "execute_tasks", execute_tasks)
    return files


async def download(tweets, tmp_path):
    downloader = TwitterDownloader(dict(KWARGS))
    await downloader.create_download_tasks(dict(KWARGS), tweets, tmp_path)
    await downloader.close()


async def test_mixed_media_downloads_photos_and_video(downloads, tmp_path):
    # 此前只按第一个媒体的类型处理：先是图片时视频只得到缩略图
    page = timeline(tweet("1", photo("a"), video("v"), photo("b")))

    await download(PostTweetFilter(page)._to_list(), tmp_path)

    assert downloads == [
        ("1_image_1.jpg", "https://pbs.twimg.com/media/a.jpg?format=jpg&name=large"),
        ("1_image_2.jpg", "https://pbs.twimg.com/media/b.jpg?format=jpg&name=large"),
        ("1_video.mp4", "https://v/v-720.mp4"),
    ]


async def test_each_video_gets_its_own_file(downloads, tmp_path):
    page = timeline(tweet("2", video("x"), video("y", "animated_gif")))

    await download(PostTweetFilter(page)._to_list(), tmp_path)

    assert downloads == [
        ("2_video_1.mp4", "https://v/x-720.mp4"),
        ("2_video_2.mp4", "https://v/y-720.mp4"),
    ]


async def test_single_video_keeps_its_file_name(downloads, tmp_path):
    page = timeline(tweet("3", video("z")))

    await download(PostTweetFilter(page)._to_list(), tmp_path)

    assert downloads == [("3_video.mp4", "https://v/z-720.mp4")]


async def test_detail_with_two_videos_downloads_both(downloads, tmp_path):
    # 推文详情的媒体类型有多个时是列表，此前既不当视频也不当图片，一个都不下载
    result = tweet("4", video("p"), video("q"))
    data = {
        "data": {
            "threaded_conversation_with_injections_v2": {
                "instructions": [
                    {"type": "TimelineAddEntries", "entries": [entry(result)]}
                ]
            }
        }
    }

    await download(TweetDetailFilter(data, "4")._to_dict(), tmp_path)

    assert downloads == [
        ("4_video_1.mp4", "https://v/p-720.mp4"),
        ("4_video_2.mp4", "https://v/q-720.mp4"),
    ]
