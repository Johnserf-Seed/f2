# path: tests/test_dl.py

import asyncio

from f2.apps.douyin.dl import DouyinDownloader


async def main():
    url = "http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4"
    save_paths = "tests/video"
    downloader = DouyinDownloader()
    await downloader.initiate_download("视频", url, save_paths, "big_buck_bunny", ".mp4")


asyncio.run(main())
