# path: tests/test_weibo_images.py

import pytest

from f2.apps.weibo.dl import WeiboDownloader
from f2.apps.weibo.filter import UserWeiboFilter, WeiboDetailFilter

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
