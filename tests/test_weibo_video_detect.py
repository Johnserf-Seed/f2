# path: tests/test_weibo_video_detect.py

import pytest

from f2.apps.weibo.dl import WeiboDownloader
from f2.apps.weibo.filter import UserWeiboFilter, WeiboDetailFilter


async def downloaded(tmp_path, weibo_data_dict):
    """交给下载器后依次调用了哪些下载方法"""
    downloader = WeiboDownloader({"cookie": "a=b"})
    called = []

    async def record(name):
        called.append(name)

    downloader.download_desc = lambda: record("desc")
    downloader.download_video = lambda: record("video")
    downloader.download_images = lambda: record("images")

    await downloader.handler_download(
        {"cookie": "a=b", "folderize": False}, weibo_data_dict, tmp_path
    )
    await downloader.close()
    return called


@pytest.mark.parametrize("pic_ids", [[], None])
@pytest.mark.parametrize(
    "is_video, expected",
    [(11, "video"), ("11", "video"), (None, "images"), ("1", "images")],
)
async def test_weibo_video_type_accepts_int_and_str(
    tmp_path, pic_ids, is_video, expected
):
    # 视频的 page_info.type 既可能是整数 11，也可能是字符串 "11"（#249、#359）；
    # 视频微博的 pic_ids 是空列表，此前只认 None
    called = await downloaded(
        tmp_path,
        {
            "uid": "1",
            "weibo_id": "2",
            "weibo_pic_num": 0,
            "weibo_pic_ids": pic_ids,
            "is_video": is_video,
        },
    )

    assert called == ["desc", expected]


def status(**extra):
    """与接口相同结构的微博（只保留用到的字段）"""
    return {
        "idstr": "5348816993124629",
        "mblogid": "RktX5d6Rf",
        "created_at": "Sun Oct 05 10:00:00 +0800 2026",
        "text_raw": "测试微博",
        "user": {"idstr": "1839167003", "screen_name": "测试用户"},
        **extra,
    }


VIDEO = status(
    pic_ids=[],
    pic_num=0,
    page_info={
        "type": "11",
        "object_type": "video",
        "media_info": {
            "playback_list": [
                {"play_info": {"url": "https://f.video.weibocdn.com/1.mp4"}}
            ]
        },
    },
)
PHOTOS = status(pic_ids=["870dd2b6gy1h6ldat37sfj20zj1be78j"], pic_num=1)


@pytest.mark.parametrize("mode", ["one", "post"])
@pytest.mark.parametrize(
    "weibo, expected", [(VIDEO, "video"), (PHOTOS, "images")], ids=["video", "photos"]
)
async def test_weibo_media_type_from_api_data(tmp_path, mode, weibo, expected):
    # #249：视频微博的 pic_ids 是空列表，单条微博的 is_video 还按列表取值（["11"]），
    # 此前两种模式下视频都提示“该微博无法下载，需要在微博客户端查看”
    if mode == "one":
        data = WeiboDetailFilter({"ok": 1, **weibo})._to_dict()
    else:
        [data] = UserWeiboFilter({"ok": 1, "data": {"list": [weibo]}})._to_list()

    assert await downloaded(tmp_path, data) == ["desc", expected]
