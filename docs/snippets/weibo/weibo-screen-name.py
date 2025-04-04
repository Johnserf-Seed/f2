# region single-weibo-screen_name-snippet
import asyncio

from f2.apps.weibo.utils import WeiboScreenNameFetcher
from f2.log.logger import logger


async def main():
    raw_url = "https://weibo.com/n/自我充电功能丧失"
    return await WeiboScreenNameFetcher.get_weibo_screen_name(raw_url)


if __name__ == "__main__":
    logger.info(asyncio.run(main()))

# endregion single-weibo-screen_name-snippet


# region multi-weibo-screen_name-snippet
import asyncio

from f2.apps.weibo.utils import WeiboScreenNameFetcher
from f2.log.logger import logger
from f2.utils.string.formatter import extract_valid_urls


async def main():
    raw_urls = [
        "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1",
        "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/",
        "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1?test=123",
        "https://weibo.com/n/%E8%87%AA%E6%88%91%E5%85%85%E7%94%B5%E5%8A%9F%E8%83%BD%E4%B8%A7%E5%A4%B1/?test=123",
        "https://weibo.com/n/自我充电功能丧失",
        "https://weibo.com/n/自我充电功能丧失/",
        "https://weibo.com/n/自我充电功能丧失?test=123",
        "https://weibo.com/n/自我充电功能丧失/?test=123",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await WeiboScreenNameFetcher.get_all_weibo_screen_name(urls)


if __name__ == "__main__":
    logger.info(asyncio.run(main()))

# endregion multi-weibo-screen_name-snippet
