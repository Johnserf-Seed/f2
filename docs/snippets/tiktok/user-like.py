import asyncio
from f2.apps.tiktok.handler import fetch_user_like_videos
from f2.apps.tiktok.utils import SecUserIdFetcher


async def main():
    secUid = await SecUserIdFetcher.get_secuid("")  # 替换开放喜欢列表的用户主页
    print([aweme_data_list async for aweme_data_list in fetch_user_like_videos(secUid)])


if __name__ == "__main__":
    asyncio.run(main())
