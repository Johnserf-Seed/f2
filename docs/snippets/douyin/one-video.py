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
    video = await DouyinHandler(kwargs).fetch_one_video(aweme_id="7294994585925848359")
    print("=================_to_raw================")
    print(video._to_raw())
    # print("=================_to_dict================")
    # print(video._to_dict())
    # print("=================_to_list================")
    # print(video._to_list())


if __name__ == "__main__":
    asyncio.run(main())
