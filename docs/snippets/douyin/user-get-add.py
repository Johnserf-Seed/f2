import asyncio
from f2.apps.douyin.handler import get_or_add_user_data

async def main():
    kwargs = {"path": "Download"}
    async with AsyncUserDB("douyin_users.db") as audb:
        sec_user_id="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
        print(await get_or_add_user_data(kwargs=kwargs, sec_user_id=sec_user_id, db=audb))

if __name__ == "__main__":
    asyncio.run(main())
