import asyncio
from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
    "timeout": 10,
}


async def main():
    async for aweme_data_list in DouyinHandler(kwargs).fetch_user_collection_videos():
        print("=================_to_raw================")
        print(aweme_data_list._to_raw())
        # print("=================_to_dict===============")
        # print(aweme_data_list._to_dict())
        # print("=================_to_list===============")
        # print(aweme_data_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
