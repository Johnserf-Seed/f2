// #region create-user-folder
from f2.apps.douyin.utils import create_user_folder


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
    "path": "Download",
    "mode": "post",
}


if __name__ == "__main__":
    current_nickname = "New Nickname"
    print(create_user_folder(kwargs, current_nickname))
    # X:\......\Download\douyin\post\New Nickname

// #endregion create-user-folder


// #region rename-user-folder
import asyncio
from f2.apps.douyin.db import AsyncUserDB
from f2.apps.douyin.utils import rename_user_folder
from f2.apps.douyin.handler import DouyinHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http": None, "https": None},
    "cookie": "YOUR_COOKIE_HERE",
    "path": "Download",
    "mode": "post",
}


async def main():
    sec_user_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"

    async with AsyncUserDB("douyin_users.db") as audb:
        local_user_path = await DouyinHandler(kwargs).get_or_add_user_data(
            kwargs, sec_user_id, audb
        )
    print(local_user_path)
    # X:\......\Download\douyin\post\songzhen

    current_nickname = "New Nickname"
    new_user_path = rename_user_folder(local_user_path, current_nickname)
    print(new_user_path)
    # X:\......\Download\douyin\post\New Nickname

if __name__ == "__main__":
    asyncio.run(main())

// #endregion rename-user-folder