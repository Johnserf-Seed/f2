import asyncio
from f2.apps.douyin.handler import fetch_one_video, fetch_user_mix_videos

async def main():
    mix_id = await fetch_one_video(aweme_id="7294914031133969705").get("mix_id")
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_collect_videos(mix_id)
    ]
    print(results)
    print("-------------------")
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_collect_videos(mix_id, 0, 10, 20)
    ]
    print(results)

if __name__ == "__main__":
    asyncio.run(main())