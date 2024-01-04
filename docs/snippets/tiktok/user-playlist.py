import asyncio
from f2.apps.tiktok.handler import fetch_play_list
from f2.apps.tiktok.utils import SecUserIdFetcher


async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___")
    print([aweme_data_list async for aweme_data_list in fetch_play_list(secUid)])


if __name__ == "__main__":
    asyncio.run(main())
