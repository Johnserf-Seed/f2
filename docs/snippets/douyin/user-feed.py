import asyncio
from f2.apps.douyin.handler import DouyinHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    sec_user_id = ""  # 用户ID
    async for feeds in DouyinHandler(kwargs).fetch_user_feed_videos(
        sec_user_id, 0, 10, 20
    ):
        print("=================_to_raw================")
        print(feeds._to_raw())
        # print("=================_to_dict===============")
        # print(feeds._to_dict())
        # print("=================_to_list===============")
        # print(feeds._to_list())


if __name__ == "__main__":
    asyncio.run(main())
