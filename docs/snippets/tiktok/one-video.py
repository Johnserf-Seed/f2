import asyncio
from f2.apps.tiktok.handler import TiktokHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    video = await TiktokHandler(kwargs).fetch_one_video(itemId="7095819783324601605")
    print("=================_to_raw================")
    print(video._to_raw())
    # print("=================_to_dict================")
    # print(video._to_dict())
    # print("=================_to_list================")
    # print(video._to_list())


if __name__ == "__main__":
    asyncio.run(main())
