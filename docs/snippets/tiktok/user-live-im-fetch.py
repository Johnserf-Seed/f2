import asyncio
from f2.apps.tiktok.handler import TiktokHandler


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
        "Content-Type": "application/x-www-form-urlencoded;",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "GUEST_COOKIE_HERE",
}


kwargs2 = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Upgrade": "websocket",
        "Connection": "Upgrade",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "GUEST_COOKIE_HERE",
}


async def main():
    # 通过该接口获取wss所需的cursor和internal_ext
    live_im = await TiktokHandler(kwargs).fetch_live_im(room_id="7404848324131638062")
    # logger.info(
    #     "直播间IM页码：",
    #     live_im.cursor,
    #     "直播间IM扩展：",
    #     live_im.internalExt,
    #     "直播间IM wrss：",
    #     live_im.routeParams.wrss,
    # )

    # # 获取直播弹幕
    await TiktokHandler(kwargs2).fetch_live_danmaku(
        room_id="7404848324131638062",
        internal_ext=live_im.internalExt,
        cursor=live_im.cursor,
        wrss=live_im.routeParams.wrss,
    )


if __name__ == "__main__":
    asyncio.run(main())
