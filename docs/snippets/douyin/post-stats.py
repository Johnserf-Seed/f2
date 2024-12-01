import asyncio
from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.utils import TokenManager
from f2.log.logger import logger


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "cookie": f"mstoken={TokenManager.gen_real_msToken()}; ttwid={TokenManager.gen_ttwid()};",
    "proxies": {"http://": None, "https://": None},
}


async def main():
    success_count, faild_count = 0, 0

    for i in range(10000):
        logger.info(f"第 {i+1} 次请求")
        stats = await DouyinHandler(kwargs).fetch_post_stats(
            aweme_id="7436713470965468474", aweme_type=68
        )
        if stats.status_code == 0:
            success_count += 1
            logger.debug("作品播放量已增加")
        else:
            faild_count += 1
            logger.warning(stats.status_msg)

        logger.info(f"播放量增加成功 {success_count} 次，失败 {faild_count} 次")
        # await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
