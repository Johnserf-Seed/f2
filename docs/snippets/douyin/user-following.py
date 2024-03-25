import asyncio
from f2.log.logger import logger
from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {
        "http": None,
        "https": None,
    },
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    sec_user_id = ""  # 公开关注的账号
    # sec_user_id = "MS4wLjABAAAAGPm-wPeGQuziCu5z6KerQA7WmSTnS99c8lU8WLToB0BsN02mqbPxPuxwDjKf7udZ"  # 隐私设置的账号
    async for following in DouyinHandler(kwargs).fetch_user_following(
        sec_user_id=sec_user_id
    ):
        logger.info(
            "用户ID：{0} 用户昵称：{1} 用户作品数：{2} 额外内容：{3}".format(
                following.sec_uid,
                following.nickname,
                following.aweme_count,
                following.secondary_text,
            )
        )
        # print("=================_to_raw==================")
        # print(following._to_raw())
        # print("=================_to_dict=================")
        # print(following._to_dict())
        # print("=================_to_list===============")
        # 数据量多的情况下_to_list这种数据结构比较慢
        # print(following._to_list())


if __name__ == "__main__":
    asyncio.run(main())
