import asyncio
from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "timeout": 10,
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    aweme_id = "7463864388999466298"
    comment_id = "7464181836018893579"
    async for comment_reply_data_list in DouyinHandler(kwargs).fetch_post_comment_reply(
        aweme_id, comment_id, 0, 3, 10
    ):
        print("=================_to_raw================")
        print(comment_reply_data_list._to_raw())
        # print("=================_to_dict===============")
        # print(comment_reply_data_list._to_dict())
        # print("=================_to_list===============")
        # print(comment_reply_data_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
