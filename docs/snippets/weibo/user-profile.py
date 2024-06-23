import asyncio
from f2.apps.weibo.handler import WeiboHandler
from f2.log.logger import logger


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.weibo.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    user = await WeiboHandler(kwargs).fetch_user_info(uid="2265830070")
    logger.info(
        f"微博用户ID: {user.uid}, 昵称: {user.nickname}, 性别: {user.gender}, 地区: {user.location}, 关注数: {user.friends_count}, 粉丝数: {user.followers_count}, 微博数: {user.weibo_count}, 个人主页: {user.profile_url}"
    )


if __name__ == "__main__":
    asyncio.run(main())
