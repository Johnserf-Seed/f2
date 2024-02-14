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
    secUid = (
        "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
    )
    uniqueId = "vantoan___"
    print(await TiktokHandler(kwargs).handler_user_profile(secUid=secUid))
    print("-------------------")
    print(await TiktokHandler(kwargs).handler_user_profile(uniqueId=uniqueId))


if __name__ == "__main__":
    asyncio.run(main())
