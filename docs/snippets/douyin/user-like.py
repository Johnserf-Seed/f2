import asyncio
from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": "YOUR_COOKIE_HERE",
    "timeout": 10,
    "proxies": {"http://": None, "https://": None},
}


async def main():
    sec_user_id = "MS4wLjABAAAAW9FWcqS7RdQAWPd2AA5fL_ilmqsIFUCQ_Iym6Yh9_cUa6ZRqVLjVQSUjlHrfXY1Y"  # 开放喜欢列表的sec_user_id
    # sec_user_id = "MS4wLjABAAAAkA9Zsx7wNHUWse8xwUt9zzlAUfZ-7ZOBMbPzKhkDYEjUd-f4qS_DM6fNyxP_-9l2"  # 未开放喜欢列表的sec_user_id
    async for aweme_data_list in DouyinHandler(kwargs).fetch_user_like_videos(
        sec_user_id, 0, 10, 20
    ):
        print("=================_to_raw================")
        print(aweme_data_list._to_raw())
        # print("=================_to_dict===============")
        # print(aweme_data_list._to_dict())
        # print("=================_to_list===============")
        # print(aweme_data_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
