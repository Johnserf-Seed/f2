// #region create-user-folder
from f2.apps.tiktok.utils import create_user_folder

if __name__ == "__main__":
    kwargs = {"path": "Download"}
    current_nickname = "New Nickname"
    print(create_user_folder(kwargs, current_nickname))
    # X:\......\Download\tiktok\PLEASE_SETUP_MODE\New Nickname

    kwargs = {"path": "Download", "mode": "post"}
    print(create_user_folder(kwargs, current_nickname))
    # X:\......\Download\tiktok\post\New Nickname

// #endregion create-user-folder


// #region rename-user-folder
import asyncio
from f2.apps.tiktok.db import AsyncUserDB
from f2.apps.tiktok.utils import rename_user_folder
from f2.apps.tiktok.handler import get_or_add_user_data

async def main():
    kwargs = {"path": "Download", "mode": "post"}
    sec_user_id = "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"

    async with AsyncUserDB("tiktok_users.db") as audb:
        local_user_path = await get_or_add_user_data(kwargs, sec_user_id, audb)
    print(local_user_path)
    # X:\......\Download\tiktok\post\vantoan___

    current_nickname = "New Nickname"
    new_user_path = rename_user_folder(local_user_path, current_nickname)
    print(new_user_path)
    # X:\......\Download\tiktok\post\New Nickname

if __name__ == "__main__":
    asyncio.run(main())

// #endregion rename-user-folder