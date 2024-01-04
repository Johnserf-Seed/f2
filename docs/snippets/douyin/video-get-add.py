import asyncio
from f2.apps.douyin.handler import get_or_add_video_data, fetch_one_video
from f2.apps.douyin.db import AsyncVideoDB

# 需要忽略的字段（需过滤掉有时效性的字段）
ignore_fields = ["video_play_addr", "images", "video_bit_rate", "cover"]


async def main():
    aweme_data = await fetch_one_video(aweme_id="7294994585925848359")
    async with AsyncVideoDB("douyin_videos.db") as avdb:
        await get_or_add_video_data(aweme_data, avdb, ignore_fields)


if __name__ == "__main__":
    asyncio.run(main())
