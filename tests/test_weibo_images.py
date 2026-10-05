# path: tests/test_weibo_images.py

import pytest

from f2.apps.weibo.dl import WeiboDownloader
from f2.apps.weibo.filter import UserWeiboFilter, WeiboDetailFilter
from f2.apps.weibo.utils import mix_media_video_urls

GIF = "75c25feagy1ihpixwus1tg20qo0k0nps"
JPG = "870dd2b6gy1h6ldat37sfj20zj1be78j"
LIVE = "006aOAZbgy1ihpj2s3v0yj30u01hcq7k"

# 与接口相同结构的图片微博（只保留用到的字段）
WEIBO = {
    "idstr": "5350000000000000",
    "mblogid": "Rl0hcsrHX",
    "created_at": "Sun Oct 05 10:00:00 +0800 2026",
    "text_raw": "动图",
    "user": {"idstr": "1975672810", "screen_name": "测试用户"},
    "pic_num": 3,
    "pic_ids": [GIF, JPG, LIVE],
    "pic_infos": {
        GIF: {"type": "gif"},
        JPG: {"type": "pic"},
        LIVE: {"type": "livephoto"},
    },
}


@pytest.mark.parametrize("mode", ["one", "post"])
async def test_gif_pictures_keep_gif_suffix(tmp_path, monkeypatch, mode):
    # 动图的原图是 GIF（实测 Content-Type 为 image/gif），此前一律存成 .jpg
    if mode == "one":
        data = WeiboDetailFilter({"ok": 1, **WEIBO})._to_dict()
    else:
        [data] = UserWeiboFilter({"ok": 1, "data": {"list": [WEIBO]}})._to_list()

    saved = []

    async def record(self, label, url, base_path, name, suffix, *args, **kwargs):
        saved.append((url.rsplit("/", 1)[-1], name.rsplit("_", 1)[-1], suffix))

    monkeypatch.setattr(WeiboDownloader, "initiate_download", record)
    downloader = WeiboDownloader({"cookie": "a=b"})
    downloader.kwargs = {"naming": "{create}_{desc}"}
    downloader.weibo_id = WEIBO["idstr"]
    downloader.weibo_data_dict = data
    downloader.base_path = tmp_path

    await downloader.download_images()
    await downloader.close()

    assert saved == [(GIF, "1", ".gif"), (JPG, "2", ".jpg"), (LIVE, "3", ".jpg")]


async def test_missing_pic_infos_falls_back_to_jpg(tmp_path, monkeypatch):
    saved = []

    async def record(self, label, url, base_path, name, suffix, *args, **kwargs):
        saved.append(suffix)

    monkeypatch.setattr(WeiboDownloader, "initiate_download", record)
    downloader = WeiboDownloader({"cookie": "a=b"})
    downloader.kwargs = {"naming": "{create}_{desc}"}
    downloader.weibo_id = "1"
    downloader.weibo_data_dict = {"weibo_pic_ids": [GIF], "weibo_pic_infos": None}
    downloader.base_path = tmp_path

    await downloader.download_images()
    await downloader.close()

    assert saved == [".jpg"]


# ---------------- 图片与视频混排 ----------------

JPG2 = "870dd2b6gy1h6ldat37sfj20zj1be78k"
HD = "https://f.video.weibocdn.com/hd.mp4"
SD = "https://f.video.weibocdn.com/sd.mp4"


def video_item(*urls):
    return {
        "type": "video",
        "data": {
            "media_info": {"playback_list": [{"play_info": {"url": u}} for u in urls]}
        },
    }


MIXED = WEIBO | {
    "text_raw": "混排",
    "pic_num": 2,
    "pic_ids": [JPG, JPG2],
    "pic_infos": {JPG: {"type": "pic"}, JPG2: {"type": "pic"}},
    # 与接口一致：视频在 mix_media_info 中，pic_ids 只有图片
    "mix_media_info": {
        "items": [
            video_item(HD, SD),
            {"type": "pic", "data": {"pic_id": JPG}},
            {"type": "pic", "data": {"pic_id": JPG2}},
        ]
    },
}


@pytest.mark.parametrize("mode", ["one", "post"])
async def test_mixed_media_downloads_videos_too(tmp_path, monkeypatch, mode):
    # 此前只下载 pic_ids 中的图片，混排的视频被直接丢掉
    if mode == "one":
        data = WeiboDetailFilter({"ok": 1, **MIXED})._to_dict()
    else:
        [data] = UserWeiboFilter({"ok": 1, "data": {"list": [MIXED]}})._to_list()

    saved = []

    async def record(self, label, content, base_path, name, suffix, *args, **kwargs):
        saved.append((name.split("混排", 1)[-1], suffix, content))

    monkeypatch.setattr(WeiboDownloader, "initiate_download", record)
    monkeypatch.setattr(WeiboDownloader, "initiate_static_download", record)
    downloader = WeiboDownloader({"cookie": "a=b"})

    await downloader.handler_download(
        {"cookie": "a=b", "naming": "{create}_{desc}"}, data, tmp_path
    )
    await downloader.close()

    assert [(tail, suffix) for tail, suffix, _ in saved] == [
        ("_desc", ".txt"),
        ("_image_1", ".jpg"),
        ("_image_2", ".jpg"),
        ("_video", ".mp4"),
    ]
    assert saved[-1][2] == [HD, SD]


def test_mix_media_video_urls():
    items = [
        video_item(HD, SD),
        {"type": "pic", "data": {"pic_id": JPG}},
        video_item(),  # 没有播放地址的视频跳过
        "unexpected",
        video_item(SD),
    ]

    assert mix_media_video_urls(items) == [[HD, SD], [SD]]
    assert mix_media_video_urls(None) == []
