# path: f2/apps/tiktok/api.py


class TiktokAPIEndpoints:
    """
    API Endpoints for TikTok
    """

    # 抖音域名 (Tiktok Domain)
    TIKTOK_DOMAIN = "https://www.tiktok.com"

    # 直播域名 (Webcast Domain)
    WEBCAST_DOMAIN = "https://webcast.tiktok.com"

    # WSS域名 (WSS Domain)
    WEBCAST_WSS_DOMAIN = "wss://webcast16-ws-alisg.tiktok.com"

    # 登录 (Login)
    LOGIN_ENDPOINT = f"{TIKTOK_DOMAIN}/login/"

    # 首页推荐 (Home Recommend)
    HOME_RECOMMEND = f"{TIKTOK_DOMAIN}/api/recommend/item_list/"

    # 用户详细信息 (User Detail Info)
    USER_DETAIL = f"{TIKTOK_DOMAIN}/api/user/detail/"

    # 用户作品 (User Post)
    USER_POST = f"{TIKTOK_DOMAIN}/api/post/item_list/"

    # 用户点赞 (User Like)
    USER_LIKE = f"{TIKTOK_DOMAIN}/api/favorite/item_list/"

    # 用户收藏 (User Collect)
    USER_COLLECT = f"{TIKTOK_DOMAIN}/api/user/collect/item_list/"

    # 用户播放列表 (User Play List)
    USER_PLAY_LIST = f"{TIKTOK_DOMAIN}/api/user/playlist/"

    # 用户合集 (User Mix)
    USER_MIX = f"{TIKTOK_DOMAIN}/api/mix/item_list/"

    # 猜你喜欢 (Guess You Like)
    GUESS_YOU_LIKE = f"{TIKTOK_DOMAIN}/api/related/item_list/"

    # 用户关注 (User Follow)
    # USER_FOLLOW = f"{TIKTOK_DOMAIN}/api/relation/user/list/"

    # 用户粉丝 (User Fans)
    # USER_FANS = f"{TIKTOK_DOMAIN}/api/relation/follower/list/"

    # 作品信息 (Post Detail)
    AWEME_DETAIL = f"{TIKTOK_DOMAIN}/api/item/detail/"

    # 作品评论 (Post Comment)
    POST_COMMENT = f"{TIKTOK_DOMAIN}/api/comment/list/"

    # 作品搜索 (Post Search)
    POST_SEARCH = f"{TIKTOK_DOMAIN}/api/search/item/full/"

    # 用户直播间 (User Live Room)
    USER_LIVE = f"{TIKTOK_DOMAIN}/api-live/user/room/"

    # 检查开播状态 (Check Live Status)
    CHECK_LIVE_ALIVE = f"{WEBCAST_DOMAIN}/webcast/room/check_alive/"

    # 直播弹幕初始化 (Live Danmaku Init)
    LIVE_IM_FETCH = f"{WEBCAST_DOMAIN}/webcast/im/fetch/"

    # 直播弹幕(WSS) (Live Danmaku WSS)
    LIVE_IM_WSS = f"{WEBCAST_WSS_DOMAIN}/webcast/im/ws_proxy/ws_reuse_supplement/"
