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
    user_id = "92908021676"
    # 只有开播的状态才会返回直播间id
    live_status = await DouyinHandler(kwargs).fetch_user_live_status(user_id=user_id)
    print("=================_to_raw================")
    print(live_status._to_raw())
    # print("=================_to_dict===============")
    # print(live_status._to_dict())


if __name__ == "__main__":
    asyncio.run(main())
