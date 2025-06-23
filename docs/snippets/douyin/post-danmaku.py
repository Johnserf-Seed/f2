# region post-danmaku-snippet
import asyncio

from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    aweme_id = "7519016931375746367"

    async for danmaku_data_list in DouyinHandler(kwargs).fetch_post_danmaku(
        aweme_id, 0, 50, "json", 100
    ):
        print("=================_to_raw================")
        print(danmaku_data_list._to_raw())
        # print("=================_to_dict===============")
        # print(danmaku_data_list._to_dict())
        # print("=================_to_list===============")
        # print(danmaku_data_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())

# endregion post-danmaku-snippet


# region post-time-danmaku-snippet
import asyncio

from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    aweme_id = "7519016931375746367"

    aweme_data = await DouyinHandler(kwargs).fetch_one_video(aweme_id)

    danmaku_data_list = await DouyinHandler(kwargs).fetch_post_time_danmaku(
        aweme_id=aweme_id,
        start_time=0,
        end_time=10000,
        authentication_token=aweme_data.authentication_token,
        duration=aweme_data.duration,
        format="json",
    )
    print("=================_to_raw================")
    print(danmaku_data_list._to_raw())
    # print("=================_to_dict===============")
    # print(danmaku_data_list._to_dict())
    # print("=================_to_list===============")
    # print(danmaku_data_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())

# endregion post-time-danmaku-snippet
