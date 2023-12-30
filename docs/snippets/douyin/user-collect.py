import asyncio
from f2.apps.douyin.handler import fetch_user_collect_videos

async def main():
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_collect_videos()
    ]
    print(results)
    print("-------------------")
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_collect_videos(0, 10, 20)
    ]
    print(results)

if __name__ == "__main__":
    asyncio.run(main())