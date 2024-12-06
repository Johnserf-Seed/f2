import asyncio
from f2.apps.douyin.handler import DouyinHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "YOUR_COOKIE_HERE",
    "proxies": {"http://": None, "https://": None},
}


async def main():
    async for related_list in DouyinHandler(kwargs).fetch_related_videos(
        aweme_id="7294994585925848359",
        filterGids="",
        page_counts=20,
        max_counts=20,
    ):
        print("=================_to_raw================")
        print(related_list._to_raw())
        # print("=================_to_dict================")
        # print(related_list._to_dict())
        # print("=================_to_list================")
        # print(related_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
