# path: tests/test_dl.py

import pytest
from f2.dl.base_downloader import BaseDownloader

kwargs = {
    "headers": {"User-Agent": "", "Referer": ""},
    "proxies": {"http://": None, "https://": None},
    "cookie": "",
}


# 使用 Pytest 的 asyncio 装饰器标记异步测试函数
@pytest.mark.asyncio
async def test_download_video():
    url = "http://samples.mplayerhq.hu/MPEG-4/CDR-Dinner_LAN_800k.mp4"
    save_paths = "tests/video"
    async with BaseDownloader(kwargs) as downloader:
        await downloader.initiate_download(
            "视频", url, save_paths, "big_buck_bunny", ".mp4"
        )
