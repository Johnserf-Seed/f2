import asyncio
from f2.apps.douyin.handler import DouyinHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    follow_live = await DouyinHandler(kwargs).fetch_user_following_lives()
    print("=================_to_raw================")
    print(follow_live._to_raw())
    # print("=================_to_dict===============")
    # print(follow_live._to_dict())
    # print("=================_to_list===============")
    # print(follow_live._to_list())


if __name__ == "__main__":
    asyncio.run(main())
