import asyncio
from f2.log.logger import logger
from f2.apps.douyin.handler import DouyinHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    user_id = ""  # 公开粉丝的账号
    sec_user_id = ""  # 公开粉丝的账号
    # sec_user_id = "MS4wLjABAAAAGPm-wPeGQuziCu5z6KerQA7WmSTnS99c8lU8WLToB0BsN02mqbPxPuxwDjKf7udZ"  # 隐私设置的账号

    # 至少提供 user_id 或 sec_user_id 中的一个参数
    # 根据max_time 和 min_time 区间获取用户粉丝列表
    async for follower in DouyinHandler(kwargs).fetch_user_follower(
        user_id=user_id,
        sec_user_id=sec_user_id,
        # max_time=1668606509,
        # min_time=0,
    ):
        if follower.status_code != 0:
            logger.erro("错误代码：{0} 错误消息：{1}").format(
                follower.status_code, follower.status_msg
            )
        else:
            logger.info(
                "用户ID：{0} 用户昵称：{1} 用户作品数：{2}".format(
                    follower.sec_uid, follower.nickname, follower.aweme_count
                )
            )

        # print("=================_to_raw================")
        # print(follower._to_raw())
        # print("=================_to_dict===============")
        # print(follower._to_dict())
        # print("=================_to_list===============")
        # 数据量多的情况下_to_list这种数据结构比较慢
        # print(follower._to_list())


if __name__ == "__main__":
    asyncio.run(main())
