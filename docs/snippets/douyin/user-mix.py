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
    video = await DouyinHandler(kwargs).fetch_one_video(aweme_id="7294914031133969705")

    async for mix_list in DouyinHandler(kwargs).fetch_user_mix_videos(
        video.mix_id,
        max_cursor=0,
        page_counts=10,
        max_counts=20,
    ):
        print("=================_to_raw================")
        print(mix_list._to_raw())
        # print("=================_to_dict===============")
        # print(mix_list._to_dict())
        # print("=================_to_list===============")
        # print(mix_list._to_list())


if __name__ == "__main__":
    asyncio.run(main())
