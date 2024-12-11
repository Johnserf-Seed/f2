import asyncio
from f2.apps.weibo.handler import WeiboHandler
from f2.apps.weibo.db import AsyncUserDB

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.weibo.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
    "path": "Download",
    # "mode": "post",
}


async def main():
    async with AsyncUserDB("weibo_users.db") as audb:
        uid = "6524978930"
        print(
            await WeiboHandler(kwargs).get_or_add_user_data(
                kwargs=kwargs, uid=uid, db=audb
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
