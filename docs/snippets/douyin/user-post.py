import asyncio
from f2.apps.douyin.handler import fetch_user_post_videos

async def main():
    user_sec_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_post_videos(user_sec_id)
    ]
    print(results)
    print("-------------------")
    results = [
        aweme_data_list async for aweme_data_list in fetch_user_post_videos(user_sec_id, 0, 10, 20)
    ]
    print(results)

if __name__ == "__main__":
    asyncio.run(main())