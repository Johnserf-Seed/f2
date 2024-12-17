import asyncio
from f2.apps.twitter.handler import TwitterHandler
from f2.apps.twitter.db import AsyncUserDB

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.x.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
    # "X-Csrf-Token": "",
    "path": "Download",
    # "mode": "post",
}


async def main():
    async with AsyncUserDB("twitter_users.db") as audb:
        uniqueId = "realDonaldTrump"
        print(
            await TwitterHandler(kwargs).get_or_add_user_data(
                kwargs=kwargs, uniqueId=uniqueId, db=audb
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
