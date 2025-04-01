# region user-collects-snippet
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
    async for collects in DouyinHandler(kwargs).fetch_user_collects(
        max_cursor=0,
        page_counts=10,
        max_counts=20,
    ):
        print("=================_to_raw================")
        print(collects._to_raw())
        # print("=================_to_dict===============")
        # print(collects._to_dict())


if __name__ == "__main__":
    asyncio.run(main())

# endregion user-collects-snippet


# region user-collects-videos-snippet
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
    collects_id = ""  # 收藏夹ID，通过fetch_user_collects方法获取
    async for collects_list in DouyinHandler(kwargs).fetch_user_collects_videos(
        collects_id,
        max_cursor=0,
        page_counts=10,
    ):
        print("=================_to_raw================")
        print(collects_list._to_raw())
        # print("=================_to_dict===============")
        # print(collects_list._to_dict())
        # print("=================_to_list===============")
        # print(collects_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())

# endregion user-collects-videos-snippet
