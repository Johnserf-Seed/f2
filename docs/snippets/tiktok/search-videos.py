import asyncio

from f2.apps.tiktok.handler import TiktokHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    async for search_list in TiktokHandler(kwargs).fetch_search_videos(
        keyword="Apple",
        offset=0,
        page_counts=30,
    ):
        print("=================_to_raw================")
        print(search_list._to_raw())
        # print("=================_to_dict================")
        # print(search_list._to_dict())
        # print("=================_to_list================")
        # print(search_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
