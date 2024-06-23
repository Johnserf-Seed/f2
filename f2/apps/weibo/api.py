# path: f2/apps/weibo/api.py


class WeiboAPIEndpoints:
    """
    API Endpoints for Weibo
    """

    # Weibo Domain
    WEIBO_DOMAIN = "https://weibo.com"

    # Weibo img domain
    WEIBO_IMG_DOMAIN = "https://wx4.sinaimg.cn"

    # 未读好友时间轴 / 全部
    UNREAD_FRIENDS_TIMELINE = "/ajax/feed/unreadfriendstimeline"

    # 原创微博
    ORIGINAL_WEIBO = f"{WEIBO_DOMAIN}/ajax/feed/friendstimeline"

    # 视频微博
    VIDEO_WEIBO = f"{WEIBO_DOMAIN}/ajax/feed/friendstimeline"

    # 最新微博
    NEWEST_WEIBO = f"{WEIBO_DOMAIN}/ajax/feed/friendstimeline"

    # 特别关注
    SPECIAL_WEIBO = f"{WEIBO_DOMAIN}/ajax/feed/groupstimeline"

    # 好友圈
    FRIENDS_TIMELINE = f"{WEIBO_DOMAIN}/ajax/feed/groupstimeline"

    # 超话社区
    SUPER_TOPIC = f"{WEIBO_DOMAIN}/ajax/feed/groupstimeline"

    # 单条微博
    WeiboDetail = f"{WEIBO_DOMAIN}/ajax/statuses/show"

    # 微博评论
    WEIBO_COMMENTS = f"{WEIBO_DOMAIN}/ajax/statuses/buildComments"

    # 个人信息
    USER_INFO = f"{WEIBO_DOMAIN}/ajax/profile/info"

    # 个人详情
    USER_DETAIL = f"{WEIBO_DOMAIN}/ajax/profile/detail"

    # 个人微博
    USER_WEIBO = f"{WEIBO_DOMAIN}/ajax/statuses/mymblog"

    # 个人关注
    USER_FOLLOW = f"{WEIBO_DOMAIN}/ajax/friendships/friends"

    # 个人粉丝
    USER_FANS = f"{WEIBO_DOMAIN}/ajax/friendships/friends"

    # 个人收藏
    USER_FAVORITES = f"{WEIBO_DOMAIN}/ajax/favorites/all_fav"

    # IMG
    THUMBNAIL = f"{WEIBO_IMG_DOMAIN}/wap180"

    BMIIDDLE = f"{WEIBO_IMG_DOMAIN}/wap360"

    LARGE = f"{WEIBO_IMG_DOMAIN}/orj960"

    ORIGINAL = f"{WEIBO_IMG_DOMAIN}/orj1080"

    # 原图
    LARGEST = f"{WEIBO_IMG_DOMAIN}/large"

    MW2000 = f"{WEIBO_IMG_DOMAIN}/mw2000"

    LARGE_COVER = f"{WEIBO_IMG_DOMAIN}/cmw960"
