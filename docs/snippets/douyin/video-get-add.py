import asyncio
from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.db import AsyncVideoDB

# 需要忽略的字段（需过滤掉有时效性的字段）
ignore_fields = ["video_play_addr", "images", "video_bit_rate", "cover"]

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    aweme_data = await DouyinHandler(kwargs).fetch_one_video(
        aweme_id="7294994585925848359"
    )
    async with AsyncVideoDB("douyin_videos.db") as avdb:
        await DouyinHandler(kwargs).get_or_add_video_data(
            aweme_data._to_dict(), avdb, ignore_fields
        )


if __name__ == "__main__":
    asyncio.run(main())
