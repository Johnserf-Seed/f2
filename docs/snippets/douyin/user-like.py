import asyncio
from f2.apps.douyin.handler import fetch_user_like_videos


async def main():
    user_sec_id = ""  # 替换开放喜欢列表的sec_user_id
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_like_videos(user_sec_id)
    ]
    print(results)
    print("-------------------")
    results = [
        aweme_data_list
        async for aweme_data_list in fetch_user_like_videos(user_sec_id, 0, 10, 20)
    ]
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
