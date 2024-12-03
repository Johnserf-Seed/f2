import asyncio
from f2.apps.douyin.handler import handle_sso_login


async def main():
    await handle_sso_login()


if __name__ == "__main__":
    asyncio.run(main())
