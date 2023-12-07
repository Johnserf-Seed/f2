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

    # SSO域名 (SSO Domain)
    SSO_DOMAIN = "https://sso.douyin.com"

    # WSS域名 (WSS Domain)
    WEBCAST_WSS_DOMAIN = "wss://webcast5-ws-web-lf.douyin.com"

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

    # 合集作品
    MIX_AWEME = f"{DOUYIN_DOMAIN}/aweme/v1/web/mix/aweme/"

    # 用户历史 (User History)
    USER_HISTORY = f"{DOUYIN_DOMAIN}/aweme/v1/web/history/read/"

    # 用户收藏 (User Collection)
    USER_COLLECTION = f"{DOUYIN_DOMAIN}/aweme/v1/web/aweme/listcollection/"

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

    # 直播用户信息 (Live User Info)
    LIVE_USER_INFO = f"{LIVE_DOMAIN}/webcast/user/me/"

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
