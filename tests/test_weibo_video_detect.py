# path: tests/test_weibo_video_detect.py

import pytest

from f2.apps.weibo.dl import WeiboDownloader


@pytest.mark.parametrize(
    "is_video, expected",
    [(11, "video"), ("11", "video"), (None, "images"), ("1", "images")],
)
async def test_weibo_video_type_accepts_int_and_str(tmp_path, is_video, expected):
    # 视频的 page_info.type 既可能是整数 11，也可能是字符串 "11"（#249、#359）
    downloader = WeiboDownloader({"cookie": "a=b"})
    called = []

    async def record(name):
        called.append(name)

    downloader.download_desc = lambda: record("desc")
    downloader.download_video = lambda: record("video")
    downloader.download_images = lambda: record("images")

    await downloader.handler_download(
        {"cookie": "a=b", "folderize": False},
        {
            "uid": "1",
            "weibo_id": "2",
            "weibo_pic_num": 0,
            "weibo_pic_ids": None,
            "is_video": is_video,
        },
        tmp_path,
    )

    assert called == ["desc", expected]
