import asyncio

from f2.apps.tiktok.handler import TiktokHandler
from f2.apps.tiktok.utils import SecUserIdFetcher

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    secUid = await SecUserIdFetcher.get_secuid("https://www.tiktok.com/@vantoan___")
    playlist = await TiktokHandler(kwargs).fetch_play_list(secUid, 0, 30)
    print("=================_to_raw================")
    print(playlist._to_raw())
    # print("=================_to_dict===============")
    # print(aweme_data_list._to_dict())


if __name__ == "__main__":
    asyncio.run(main())
