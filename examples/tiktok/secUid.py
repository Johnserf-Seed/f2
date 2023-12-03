import asyncio
from f2.apps.tiktok.utils import SecUserIdFetcher


async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___")
    print(secUid)


if __name__ == "__main__":
    asyncio.run(main())
