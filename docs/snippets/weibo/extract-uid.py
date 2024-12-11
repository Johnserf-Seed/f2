import asyncio
from f2.apps.weibo.handler import WeiboHandler
from f2.log.logger import logger

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.weibo.com/",
    },
    "proxies": {"http://": None, "https://": None},
}


async def main():
    uid = await WeiboHandler(kwargs).extract_weibo_uid(
        url="https://weibo.com/u/2265830070"
    )
    logger.info(f"微博用户ID: {uid}")


if __name__ == "__main__":
    asyncio.run(main())
