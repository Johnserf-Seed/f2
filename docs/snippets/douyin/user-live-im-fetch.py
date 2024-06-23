import asyncio

from f2.apps.douyin.handler import DouyinHandler

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.douyin.com/",
        "Content-Type": "application/protobuffer;",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "YOUR_COOKIE_HERE",
}

kwargs2 = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Upgrade": "websocket",
        "Connection": "Upgrade",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": "DO_NOT_USE_COOKIE_HERE",
}


async def main():
    # 获取游客ttwid的user_unique_id，你可以通过TokenManager.gen_ttwid()生成新的游客ttwid
    user = await DouyinHandler(kwargs).fetch_query_user()
    # print(user.user_unique_id)

    # 通过此接口获取room_id，参数为live_id
    room = await DouyinHandler(kwargs).fetch_user_live_videos("662122193366")
    # print(room.room_id)

    # 通过该接口获取wss所需的cursor和internal_ext
    live_im = await DouyinHandler(kwargs).fetch_live_im(
        room_id=room.room_id, unique_id=user.user_unique_id
    )
    # print(live_im.cursor, live_im.internal_ext)

    # 获取直播弹幕
    await DouyinHandler(kwargs2).fetch_live_danmaku(
        room_id=room.room_id,
        user_unique_id=user.user_unique_id,
        internal_ext=live_im.internal_ext,
        cursor=live_im.cursor,
    )


if __name__ == "__main__":
    asyncio.run(main())
