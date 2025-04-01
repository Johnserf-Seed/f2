import asyncio

from f2.apps.tiktok.db import AsyncUserDB
from f2.apps.tiktok.handler import TiktokHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
    "path": "Download",
}


async def main():
    async with AsyncUserDB("tiktok_users.db") as audb:
        secUid = "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
        print(
            await TiktokHandler(kwargs).get_or_add_user_data(
                kwargs=kwargs, secUid=secUid, db=audb
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
