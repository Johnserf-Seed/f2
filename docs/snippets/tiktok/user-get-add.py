import asyncio
from f2.apps.tiktok.handler import get_or_add_user_data
from f2.apps.tiktok.db import AsyncUserDB


async def main():
    kwargs = {"path": "Download"}
    async with AsyncUserDB("douyin_users.db") as audb:
        secUid = "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
        print(await get_or_add_user_data(kwargs=kwargs, secUid=secUid, db=audb))


if __name__ == "__main__":
    asyncio.run(main())
