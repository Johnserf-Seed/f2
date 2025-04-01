import asyncio

from f2.apps.weibo.utils import VisitorManager
from f2.log.logger import logger


async def main():
    visitor_cookie = await VisitorManager.gen_visitor()
    logger.info(f"visitor_cookie: {visitor_cookie}")


if __name__ == "__main__":
    asyncio.run(main())
