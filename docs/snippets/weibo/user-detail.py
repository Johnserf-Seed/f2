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
    uid = "2265830070"
    user = await WeiboHandler(kwargs).fetch_user_detail(uid=uid)
    logger.info(
        f"用户ID: {uid}, 生日: {user.birthday}, 性别: {user.gender}, 地区: {user.location}, 个性签名: {user.description_raw}, 注册时间: {user.create_at}, 视频播放次数: {user.video_play_count}"
    )


if __name__ == "__main__":
    asyncio.run(main())
