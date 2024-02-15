import asyncio
from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.db import AsyncUserDB

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    async with AsyncUserDB("douyin_users.db") as audb:
        sec_user_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
        print(
            await DouyinHandler(kwargs).get_user_nickname(
                sec_user_id=sec_user_id, db=audb
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
