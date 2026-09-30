# path: f2/apps/twitter/api.py
#
# 各端点 URL 中的哈希段是 X 前端打包时生成的 GraphQL 查询标识（queryId），
# X 发版会轮换。接口报 "Could not find query" 时，运行以下工具提取最新值并回写本文件：
#   python tools/update_twitter_queryid.py --patch


class TwitterAPIEndpoints:
    """
    API Endpoints for Twitter
    """

    # Twitter Domain
    TWITTER_DOMAIN = "https://x.com"

    API_DOMAIN = "https://x.com/i/api/graphql"

    # User Detail
    USER_PROFILE = f"{API_DOMAIN}/KybxDj9RrADIITXlGG8kpw/UserByScreenName"

    # User Post
    USER_POST = f"{API_DOMAIN}/qJy3MbaNndtzxf9IqUzxMg/UserTweets"

    # User Like
    USER_LIKE = f"{API_DOMAIN}/PgAssYGsPMMF1vVox5ysPg/Likes"

    # User Bookmark
    USER_BOOKMARK = f"{API_DOMAIN}/Glt3WAwBvNSPD-n_sqmX_A/Bookmarks"

    # Post Detail
    POST_DETAIL = f"{API_DOMAIN}/blErEeZkos5TDrWmrCp7cw/TweetDetail"
