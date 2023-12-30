import asyncio
from f2.apps.douyin.handler import handler_user_profile

async def main():
    sec_user_id="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
    print(await handler_user_profile(sec_user_id=sec_user_id))

if __name__ == "__main__":
    asyncio.run(main())