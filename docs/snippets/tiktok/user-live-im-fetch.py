import asyncio

from f2.apps.tiktok.crawler import TiktokWebSocketCrawler
from f2.apps.tiktok.handler import TiktokHandler
from f2.log.logger import logger

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.tiktok.com/",
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
    # 是否在终端显示弹幕消息
    "show_message": True,
    "cookie": "GUEST_COOKIE_HERE",
}


wss_callbacks = {
    "WebcastChatMessage": TiktokWebSocketCrawler.WebcastChatMessage,
    "WebcastMemberMessage": TiktokWebSocketCrawler.WebcastMemberMessage,
    "WebcastRoomUserSeqMessage": TiktokWebSocketCrawler.WebcastRoomUserSeqMessage,
    "WebcastGiftMessage": TiktokWebSocketCrawler.WebcastGiftMessage,
    "WebcastSocialMessage": TiktokWebSocketCrawler.WebcastSocialMessage,
    "WebcastLikeMessage": TiktokWebSocketCrawler.WebcastLikeMessage,
    "WebcastLinkMicFanTicketMethod": TiktokWebSocketCrawler.WebcastLinkMicFanTicketMethod,
    "WebcastLinkMicMethod": TiktokWebSocketCrawler.WebcastLinkMicMethod,
    "UserFanTicket": TiktokWebSocketCrawler.UserFanTicket,
    "WebcastLinkMessage": TiktokWebSocketCrawler.WebcastLinkMessage,
    "WebcastLinkMicBattle": TiktokWebSocketCrawler.WebcastLinkMicBattle,
    "WebcastLinkLayerMessage": TiktokWebSocketCrawler.WebcastLinkLayerMessage,
    "WebcastRoomMessage": TiktokWebSocketCrawler.WebcastRoomMessage,
    "WebcastOecLiveShoppingMessage": TiktokWebSocketCrawler.WebcastOecLiveShoppingMessage,  # TODO: 以下消息类型暂未实现
    # TODO: 以下消息类型暂未实现
    # WebcastOecLiveManagerMessage
    # WebcastInRoomBannerMessage
    # WebcastAnchorToolModificationMessage
}


async def main():
    room_id = "7454940010882976533"

    room = await TiktokHandler(kwargs).fetch_check_live_alive(room_id)
    if not room.is_alive[0]:
        logger.info("直播间：{0} 未开播".format(room_id))
        return

    # 通过该接口获取wss所需的cursor和internal_ext
    live_im = await TiktokHandler(kwargs).fetch_live_im(room_id=room_id)
    # logger.info(
    #     "直播间IM页码：",
    #     live_im.cursor,
    #     "直播间IM扩展：",
    #     live_im.internalExt,
    #     "直播间IM wrss：",
    #     live_im.routeParams.wrss,
    # )

    if live_im:
        # 获取直播间信息
        await TiktokHandler(kwargs2).fetch_live_danmaku(
            room_id=room_id,
            internal_ext=live_im.internalExt,
            cursor=live_im.cursor,
            wrss=live_im.routeParams.wrss,
        )


if __name__ == "__main__":
    asyncio.run(main())
