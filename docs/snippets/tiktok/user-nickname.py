import asyncio
from f2.apps.tiktok.handler import get_user_nickname
from f2.apps.tiktok.db import AsyncUserDB


async def main():
    async with AsyncUserDB("douyin_users.db") as audb:
        secUid = "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
        print(await get_user_nickname(secUid=secUid, db=audb))


if __name__ == "__main__":
    asyncio.run(main())
