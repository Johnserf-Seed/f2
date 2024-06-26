import asyncio
from f2.apps.tiktok.handler import TiktokHandler
from f2.apps.tiktok.utils import SecUserIdFetcher

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    secUid = await SecUserIdFetcher.get_secuid(
        "YOUR_HOME_PAGE"
    )  # 替换开放喜欢列表的用户主页

    async for aweme_data_list in TiktokHandler(kwargs).fetch_user_like_videos(
        secUid, 0, 10, 20
    ):
        print("=================_to_raw================")
        print(aweme_data_list._to_raw())
        # print("=================_to_dict===============")
        # print(aweme_data_list._to_dict())
        # print("=================_to_list===============")
        # print(aweme_data_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
