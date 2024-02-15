import asyncio
from f2.apps.tiktok.handler import TiktokHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    post = await TiktokHandler(kwargs).fetch_one_video(itemId="7095819783324601605")
    print(post)
    print("-------------------")
    post = await TiktokHandler(kwargs).fetch_one_video(itemId="7305827432509082913")
    print(post)


if __name__ == "__main__":
    asyncio.run(main())
