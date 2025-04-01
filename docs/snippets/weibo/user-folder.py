# region create-user-folder
from f2.apps.weibo.utils import create_user_folder

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.weibo.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
    "path": "Download",
    "mode": "post",
}


if __name__ == "__main__":
    current_nickname = "New Nickname"
    print(create_user_folder(kwargs, current_nickname))
    # X:\......\Download\weibo\post\New Nickname

# endregion create-user-folder


# region rename-user-folder
import asyncio

from f2.apps.weibo.db import AsyncUserDB
from f2.apps.weibo.handler import WeiboHandler
from f2.apps.weibo.utils import rename_user_folder

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.weibo.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
    "path": "Download",
    "mode": "post",
}


async def main():
    uid = "2265830070"
    async with AsyncUserDB("weibo_users.db") as audb:
        local_user_path = await WeiboHandler(kwargs).get_or_add_user_data(
            kwargs, uid, audb
        )
    print(local_user_path)
    # X:\......\Download\weibo\post\阿里多多酱

    current_nickname = "New Nickname"
    new_user_path = rename_user_folder(local_user_path, current_nickname)
    print(new_user_path)
    # X:\......\Download\weibo\post\New Nickname


if __name__ == "__main__":
    asyncio.run(main())

# endregion rename-user-folder
