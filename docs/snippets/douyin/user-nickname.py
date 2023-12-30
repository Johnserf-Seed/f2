import asyncio
from f2.apps.douyin.handler import get_user_nickname

async def main():
    async with AsyncUserDB("douyin_users.db") as audb:
        sec_user_id="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
        print(await get_user_nickname(sec_user_id=sec_user_id, db=audb))

if __name__ == "__main__":
    asyncio.run(main())
