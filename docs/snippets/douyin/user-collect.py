import asyncio
from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    results = [
        aweme_data_list
        async for aweme_data_list in DouyinHandler(kwargs).fetch_user_collect_videos()
    ]
    print(results)
    print("-------------------")
    results = [
        aweme_data_list
        async for aweme_data_list in DouyinHandler(kwargs).fetch_user_collect_videos(
            0, 10, 20
        )
    ]
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
