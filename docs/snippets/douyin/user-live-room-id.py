import asyncio
from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    live = await DouyinHandler(kwargs).fetch_user_live_videos_by_room_id(
        room_id="7318296342189919011"
    )
    print("=================_to_raw================")
    print(live._to_raw())
    # print("=================_to_dict===============")
    # print(live._to_dict())


if __name__ == "__main__":
    asyncio.run(main())
