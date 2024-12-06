import asyncio
from f2.apps.bark.handler import BarkHandler
from f2.log.logger import logger


kwargs = {
    "token": "YOUR_BARK_TOKEN_HERE",
    "send_method": "fetch",
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
}


async def main():
    bark = await BarkHandler(kwargs).send_quick_notification("Hello", "World")

    if not bark:
        logger.error("Bark 通知发送失败，未收到响应")
        return

    logger.info("=================_to_raw================")
    logger.info(bark._to_raw())
    # logger.info("=================_to_dict===============")
    # logger.info(bark._to_dict())


if __name__ == "__main__":
    asyncio.run(main())
