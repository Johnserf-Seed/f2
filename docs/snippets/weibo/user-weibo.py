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
    weibo = await WeiboHandler(kwargs).fetch_one_weibo(weibo_id="O8DM0BLLm")
    logger.info(
        f"微博ID: {weibo.weibo_id}, 微博文案: {weibo.desc}, 作者昵称: {weibo.nickname}, 发布时间: {weibo.create_time}"
    )


if __name__ == "__main__":
    asyncio.run(main())
