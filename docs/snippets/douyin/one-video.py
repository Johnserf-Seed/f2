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
    print(await DouyinHandler(kwargs).fetch_one_video(aweme_id="7294994585925848359"))
    print("-------------------")
    print(await DouyinHandler(kwargs).fetch_one_video(aweme_id="7305827432509082913"))


if __name__ == "__main__":
    asyncio.run(main())
