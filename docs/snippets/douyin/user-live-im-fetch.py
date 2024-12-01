import asyncio

from f2.apps.douyin.crawler import DouyinWebSocketCrawler
from f2.apps.douyin.handler import DouyinHandler
from f2.log.logger import logger


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
        "Content-Type": "application/protobuffer;",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    # 游客cookie即可，需要注意ttwid作为用户标识只可在一个直播间使用，不可多个直播间同时使用
    # 使用TokenManager.gen_ttwid()即可生成新的游客ttwid
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
    # 不需要填写cookie
    "cookie": "",
}

wss_callbacks = {
    "WebcastRoomMessage": DouyinWebSocketCrawler.WebcastRoomMessage,
    "WebcastLikeMessage": DouyinWebSocketCrawler.WebcastLikeMessage,
    "WebcastMemberMessage": DouyinWebSocketCrawler.WebcastMemberMessage,
    "WebcastChatMessage": DouyinWebSocketCrawler.WebcastChatMessage,
    "WebcastGiftMessage": DouyinWebSocketCrawler.WebcastGiftMessage,
    "WebcastSocialMessage": DouyinWebSocketCrawler.WebcastSocialMessage,
    "WebcastRoomUserSeqMessage": DouyinWebSocketCrawler.WebcastRoomUserSeqMessage,
    "WebcastUpdateFanTicketMessage": DouyinWebSocketCrawler.WebcastUpdateFanTicketMessage,
    "WebcastCommonTextMessage": DouyinWebSocketCrawler.WebcastCommonTextMessage,
    "WebcastMatchAgainstScoreMessage": DouyinWebSocketCrawler.WebcastMatchAgainstScoreMessage,
    "WebcastEcomFansClubMessage": DouyinWebSocketCrawler.WebcastEcomFansClubMessage,
    "WebcastRanklistHourEntranceMessage": DouyinWebSocketCrawler.WebcastRanklistHourEntranceMessage,
    "WebcastRoomStatsMessage": DouyinWebSocketCrawler.WebcastRoomStatsMessage,
    "WebcastLiveShoppingMessage": DouyinWebSocketCrawler.WebcastLiveShoppingMessage,
    "WebcastLiveEcomGeneralMessage": DouyinWebSocketCrawler.WebcastLiveEcomGeneralMessage,
    "WebcastProductChangeMessage": DouyinWebSocketCrawler.WebcastProductChangeMessage,
    "WebcastRoomStreamAdaptationMessage": DouyinWebSocketCrawler.WebcastRoomStreamAdaptationMessage,
    "WebcastNotifyEffectMessage": DouyinWebSocketCrawler.WebcastNotifyEffectMessage,
    "WebcastLightGiftMessage": DouyinWebSocketCrawler.WebcastLightGiftMessage,
    "WebcastProfitInteractionScoreMessage": DouyinWebSocketCrawler.WebcastProfitInteractionScoreMessage,
    "WebcastRoomRankMessage": DouyinWebSocketCrawler.WebcastRoomRankMessage,
    "WebcastFansclubMessage": DouyinWebSocketCrawler.WebcastFansclubMessage,
    "WebcastHotRoomMessage": DouyinWebSocketCrawler.WebcastHotRoomMessage,
    "WebcastLinkMicMethod": DouyinWebSocketCrawler.WebcastLinkMicMethod,
    "LinkMicMethod": DouyinWebSocketCrawler.WebcastLinkMicMethod,
    "WebcastLinkerContributeMessage": DouyinWebSocketCrawler.WebcastLinkerContributeMessage,
    "WebcastEmojiChatMessage": DouyinWebSocketCrawler.WebcastEmojiChatMessage,
    "WebcastScreenChatMessage": DouyinWebSocketCrawler.WebcastScreenChatMessage,
    "WebcastRoomDataSyncMessage": DouyinWebSocketCrawler.WebcastRoomDataSyncMessage,
    "WebcastInRoomBannerMessage": DouyinWebSocketCrawler.WebcastInRoomBannerMessage,
    "WebcastLinkMessage": DouyinWebSocketCrawler.WebcastLinkMessage,
    "WebcastBattleTeamTaskMessage": DouyinWebSocketCrawler.WebcastBattleTeamTaskMessage,
    "WebcastHotChatMessage": DouyinWebSocketCrawler.WebcastHotChatMessage,
    # TODO: 以下消息类型暂未实现
    # WebcastLinkMicArmiesMethod
    # WebcastLinkmicPlayModeUpdateScoreMessage
    # WebcastSandwichBorderMessage
    # WebcastLuckyBoxTempStatusMessage
    # WebcastLotteryEventMessage
    # WebcastLotteryEventNewMessage
    # WebcastDecorationUpdateMessage
    # WebcastDecorationModifyMethod
    # WebcastLinkSettingNotifyMessage
    # WebcastLinkMicBattleMethod
    # WebcastExhibitionChatMessage
}


async def main():
    # 获取游客ttwid的user_unique_id，你可以通过TokenManager.gen_ttwid()生成新的游客ttwid
    user = await DouyinHandler(kwargs).fetch_query_user()
    # logger.info("游客user_unique_id：", user.user_unique_id)

    # 通过此接口获取room_id，参数为live_id
    room = await DouyinHandler(kwargs).fetch_user_live_videos("277303127629")
    # logger.info("直播间ID：", room.room_id)

    if room.live_status != 2:
        logger.info("直播已结束")
        return

    # 通过该接口获取wss所需的cursor和internal_ext
    live_im = await DouyinHandler(kwargs).fetch_live_im(
        room_id=room.room_id, unique_id=user.user_unique_id
    )
    # logger.info("直播间IM页码：", live_im.cursor, "直播间IM扩展：", live_im.internal_ext)

    # 获取直播弹幕
    await DouyinHandler(kwargs2).fetch_live_danmaku(
        room_id=room.room_id,
        user_unique_id=user.user_unique_id,
        internal_ext=live_im.internal_ext,
        cursor=live_im.cursor,
        wss_callbacks=wss_callbacks,
    )


if __name__ == "__main__":
    asyncio.run(main())
