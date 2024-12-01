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
    secUid = (
        "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
    )
    uniqueId = "vantoan___"
    user = await TiktokHandler(kwargs).fetch_user_profile(secUid=secUid)
    print("=================_to_raw================")
    print(user._to_raw())
    # print("=================_to_dict===============")
    # print(user._to_dict())

    user = await TiktokHandler(kwargs).fetch_user_profile(uniqueId=uniqueId)
    print("=================_to_raw================")
    print(user._to_raw())
    # print("=================_to_dict===============")
    # print(user._to_dict())


if __name__ == "__main__":
    asyncio.run(main())
