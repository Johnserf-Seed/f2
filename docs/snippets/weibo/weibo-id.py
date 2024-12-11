# region single-weibo-id-snippet
import asyncio
from f2.apps.weibo.utils import WeiboIdFetcher
from f2.log.logger import logger


async def main():
    raw_url = "https://weibo.com/2265830070/O8DM0BLLm"
    return await WeiboIdFetcher.get_weibo_id(raw_url)


if __name__ == "__main__":
    logger.info(asyncio.run(main()))

# endregion single-weibo-id-snippet


# region multi-weibo-id-snippet
import asyncio
from f2.apps.weibo.utils import WeiboIdFetcher
from f2.utils.utils import extract_valid_urls
from f2.log.logger import logger


async def main():
    raw_urls = [
        "https://weibo.com/2265830070/O8DM0BLLm",
        "https://weibo.com/2265830070/O8DM0BLLm/",
        "https://weibo.com/2265830070/O8DM0BLLm/aasfasg",
        "https://weibo.com/2265830070/O8DM0BLLm/?test=123",
        "https://weibo.cn/2265830070/O8DM0BLLm/",
        "https://weibo.cn/status/5020595169001740/?test=123",
        "https://www.weibo.com/2265830070/5020595169001740",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await WeiboIdFetcher.get_all_weibo_id(urls)


if __name__ == "__main__":
    logger.info(asyncio.run(main()))

# endregion multi-weibo-id-snippet
