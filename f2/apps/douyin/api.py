# path: f2/apps/douyin/api.py


class DouyinAPIEndpoints:
    """
    API Endpoints for Douyin
    """

    # 抖音域名 (Douyin Domain)
    DOUYIN_DOMAIN = "https://www.douyin.com"

    # 抖音短域名 (Short Domain)
    IESDOUYIN_DOMAIN = "https://www.iesdouyin.com"

    # 直播域名 (Live Domain)
    LIVE_DOMAIN = "https://live.douyin.com"

    # 直播域名2 (Live Domain 2)
    LIVE_DOMAIN2 = "https://webcast.amemv.com"

    # SSO域名 (SSO Domain)
    SSO_DOMAIN = "https://sso.douyin.com"

    # WSS域名 (WSS Domain)
    WEBCAST_WSS_DOMAIN = "wss://webcast5-ws-web-hl.douyin.com"

    # 直播弹幕(WSS) (Live Danmaku WSS)
    LIVE_IM_WSS = f"{WEBCAST_WSS_DOMAIN}/webcast/im/push/v2/"

    # 首页Feed (Home Feed)
    TAB_FEED = f"{DOUYIN_DOMAIN}/aweme/v1/web/tab/feed/"

    # 用户短信息 (User Short Info)
    USER_SHORT_INFO = f"{DOUYIN_DOMAIN}/aweme/v1/web/im/user/info/"

    # 用户详细信息 (User Detail Info)
    USER_DETAIL = f"{DOUYIN_DOMAIN}/aweme/v1/web/user/profile/other/"

    # 作品基本 (Post Basic)
    BASE_AWEME = f"{DOUYIN_DOMAIN}/aweme/v1/web/aweme/"

    # 用户作品 (User Post)
    USER_POST = f"{DOUYIN_DOMAIN}/aweme/v1/web/aweme/post/"

    # Live作品 (Live Post)
    SLIDES_AWEME = f"{IESDOUYIN_DOMAIN}/web/api/v2/aweme/slidesinfo/"

    # 定位作品 (Post Local)
    LOCATE_POST = f"{DOUYIN_DOMAIN}/aweme/v1/web/locate/post/"

    # 搜索作品 (Post Search)
    POST_SEARCH = f"{DOUYIN_DOMAIN}/aweme/v1/web/general/search/single/"

    # 作品信息 (Post Detail)
    POST_DETAIL = f"{DOUYIN_DOMAIN}/aweme/v1/web/aweme/detail/"

    # 用户喜欢A (User Like A)
    USER_FAVORITE_A = f"{DOUYIN_DOMAIN}/aweme/v1/web/aweme/favorite/"

    # 用户喜欢B (User Like B)
    USER_FAVORITE_B = f"{IESDOUYIN_DOMAIN}/web/api/v2/aweme/like/"

    # 关注用户(User Following)
    USER_FOLLOWING = f"{DOUYIN_DOMAIN}/aweme/v1/web/user/following/list/"

    # 粉丝用户 (User Follower)
    USER_FOLLOWER = f"{DOUYIN_DOMAIN}/aweme/v1/web/user/follower/list/"

    # 合集作品
    MIX_AWEME = f"{DOUYIN_DOMAIN}/aweme/v1/web/mix/aweme/"

    # 用户历史 (User History)
    USER_HISTORY = f"{DOUYIN_DOMAIN}/aweme/v1/web/history/read/"

    # 用户收藏 (User Collection)
    USER_COLLECTION = f"{DOUYIN_DOMAIN}/aweme/v1/web/aweme/listcollection/"

    # 用户收藏夹 (User Collects)
    USER_COLLECTS = f"{DOUYIN_DOMAIN}/aweme/v1/web/collects/list/"

    # 用户收藏夹作品 (User Collects Posts)
    USER_COLLECTS_VIDEO = f"{DOUYIN_DOMAIN}/aweme/v1/web/collects/video/list/"

    # 用户音乐收藏 (User Music Collection)
    USER_MUSIC_COLLECTION = f"{DOUYIN_DOMAIN}/aweme/v1/web/music/listcollection/"

    # 首页朋友作品 (Friend Feed)
    FRIEND_FEED = f"{DOUYIN_DOMAIN}/aweme/v1/web/familiar/feed/"

    # 关注用户作品 (Follow Feed)
    FOLLOW_FEED = f"{DOUYIN_DOMAIN}/aweme/v1/web/follow/feed/"

    # 相关推荐 (Related Feed)
    POST_RELATED = f"{DOUYIN_DOMAIN}/aweme/v1/web/aweme/related/"

    # 关注用户列表直播 (Follow User Live)
    FOLLOW_USER_LIVE = f"{DOUYIN_DOMAIN}/webcast/web/feed/follow/"

    # 直播信息接口 (Live Info)
    LIVE_INFO = f"{LIVE_DOMAIN}/webcast/room/web/enter/"

    # 直播信息接口2 (Live Info 2)
    LIVE_INFO_ROOM_ID = f"{LIVE_DOMAIN2}/webcast/room/reflow/info/"

    # 直播用户信息 (Live User Info)
    LIVE_USER_INFO = f"{LIVE_DOMAIN}/webcast/user/me/"

    # 直播弹幕初始化 (Live Danmaku Init)
    LIVE_IM_FETCH = f"{LIVE_DOMAIN}/webcast/im/fetch/"

    # 推荐搜索词 (Suggest Words)
    SUGGEST_WORDS = f"{DOUYIN_DOMAIN}/aweme/v1/web/api/suggest_words/"

    # SSO登录 (SSO Login)
    SSO_LOGIN_GET_QR = f"{SSO_DOMAIN}/get_qrcode/"

    # 登录检查 (Login Check)
    SSO_LOGIN_CHECK_QR = f"{SSO_DOMAIN}/check_qrconnect/"

    # 登录确认 (Login Confirm)
    SSO_LOGIN_CHECK_LOGIN = f"{SSO_DOMAIN}/check_login/"

    # 登录重定向 (Login Redirect)
    SSO_LOGIN_REDIRECT = f"{DOUYIN_DOMAIN}/login/"

    # 登录回调 (Login Callback)
    SSO_LOGIN_CALLBACK = f"{DOUYIN_DOMAIN}/passport/sso/login/callback/"

    # 作品评论 (Post Comment)
    POST_COMMENT = f"{DOUYIN_DOMAIN}/aweme/v1/web/comment/list/"

    # 回复评论 (Reply Comment)
    POST_COMMENT_PUBLISH = f"{DOUYIN_DOMAIN}/aweme/v1/web/comment/publish"

    # 删除评论 (Delete Comment)
    POST_COMMENT_DELETE = f"{DOUYIN_DOMAIN}/aweme/v1/web/comment/delete/"

    # 点赞评论 (Like Comment)
    POST_COMMENT_DIGG = f"{DOUYIN_DOMAIN}/aweme/v1/web/comment/digg"

    # 查询用户 (Query User)
    QUERY_USER = f"{DOUYIN_DOMAIN}/aweme/v1/web/query/user/"

    # 作品状态 (Post Status)
    POST_STATS = f"{DOUYIN_DOMAIN}/aweme/v2/web/aweme/stats/"
