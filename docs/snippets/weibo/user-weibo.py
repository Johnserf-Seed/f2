import asyncio
from f2.apps.weibo.handler import WeiboHandler
from f2.log.logger import logger


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.weibo.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():

    async for weibo_list in WeiboHandler(kwargs).fetch_user_weibo(
        user_id="2265830070",
        page=1,
        feature=1,
        since_id="",
        max_counts=20,
    ):
        logger.info(
            f"微博ID: {weibo_list.weibo_id}, 微博文案: {weibo_list.weibo_desc_raw}, 作者昵称: {weibo_list.weibo_user_name_raw}, 发布时间: {weibo_list.weibo_created_at}"
        )

        # print("=================_to_raw================")
        # print(weibo_list._to_raw())
        # print("=================_to_dict===============")
        # print(weibo_list._to_dict())
        # print("=================_to_list===============")
        # print(weibo_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
