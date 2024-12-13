# region single-weibo-uid-snippet
import asyncio
from f2.apps.weibo.utils import WeiboUidFetcher
from f2.log.logger import logger


async def main():
    raw_url = "https://weibo.com/u/2265830070"
    return await WeiboUidFetcher.get_weibo_uid(raw_url)


if __name__ == "__main__":
    logger.info(asyncio.run(main()))

# endregion single-weibo-uid-snippet


# region multi-weibo-uid-snippet
import asyncio
from f2.apps.weibo.utils import WeiboUidFetcher
from f2.utils.utils import extract_valid_urls
from f2.log.logger import logger


async def main():
    raw_urls = [
        "https://weibo.com/u/2265830070",
        "https://weibo.com/u/2265830070/",
        "https://weibo.com/u/2265830070/?test=123",
        "https://weibo.com/2265830070",
        "https://weibo.com/2265830070/",
        "https://weibo.com/2265830070/?test=123",
        "https://weibo.com/2265830070/O8DM0BLLm",
        "https://weibo.com/2265830070/O8DM0BLLm/",
        "https://weibo.com/2265830070/O8DM0BLLm/?test=123",
        "https://weibo.com/2265830070/O8DM0BLLm/%$#",
        "https://weibo.com/2265830070/O8DM0BLLm/" + "a" * 2048,
        "https://m.weibo.cn/2265830070/5020595169001740",
        "https://m.weibo.cn/2265830070/5020595169001740?test=123",
        "https://m.weibo.cn/2265830070/5020595169001740/",
        "https://m.weibo.cn/2265830070/5020595169001740/?test=123",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await WeiboUidFetcher.get_all_weibo_uid(urls)


if __name__ == "__main__":
    logger.info(asyncio.run(main()))

# endregion multi-weibo-uid-snippet
