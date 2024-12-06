# region user-collection-music-snippet
import asyncio
from f2.apps.douyin.handler import DouyinHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "YOUR_COOKIE_HERE",
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
}


async def main():
    async for music_list in DouyinHandler(kwargs).fetch_user_music_collection(
        max_cursor=0,
        page_counts=20,
    ):
        print("=================_to_raw================")
        print(music_list._to_raw())
        # print("=================_to_dict===============")
        # print(music_list._to_dict())
        # print("=================_to_list===============")
        # print(music_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())

# endregion user-collection-music-snippet


# region user-collection-video-snippet
import asyncio
from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "YOUR_COOKIE_HERE",
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
}


async def main():
    async for collection_list in DouyinHandler(kwargs).fetch_user_collection_videos(
        max_cursor=0,
        page_counts=20,
    ):
        print("=================_to_raw================")
        print(collection_list._to_raw())
        # print("=================_to_dict===============")
        # print(collection_list._to_dict())
        # print("=================_to_list===============")
        # print(collection_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())

# endregion user-collection-video-snippet
