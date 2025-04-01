import asyncio

from f2.apps.twitter.handler import TwitterHandler
from f2.log.logger import logger

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.x.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
    # "X-Csrf-Token": "",
}


async def main():
    user = await TwitterHandler(kwargs).fetch_user_profile(uniqueId="realDonaldTrump")
    logger.info(
        f"昵称: {user.nickname_raw}, 注册时间: {user.join_time},  个性签名: {user.user_description_raw},  粉丝数: {user.followers_count},  关注数: {user.friends_count},  认证信息: {user.is_blue_verified}"
    )

    print("=================_to_raw================")
    print(user._to_raw())
    # print("=================_to_dict================")
    # print(video._to_dict())


if __name__ == "__main__":
    asyncio.run(main())
