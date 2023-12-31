import asyncio
from f2.apps.tiktok.handler import get_or_add_video_data
from f2.apps.tiktok.db import AsyncUserDB

# 需要忽略的字段（需过滤掉有时效性的字段）
ignore_fields = ["video_play_addr", "images", "video_bit_rate", "cover"]

async def main():
    aweme_data = await fetch_one_video(itemId="7095819783324601605")
    async with AsyncVideoDB("douyin_videos.db") as avdb:
        await get_or_add_video_data(aweme_data, avdb, ignore_fields)

if __name__ == "__main__":
    asyncio.run(main())