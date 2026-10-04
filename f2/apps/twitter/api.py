# path: f2/apps/twitter/api.py

# 网页端 GraphQL 查询的内置 queryId（取自 2026-10 的 main.js）。queryId 随 X 发版变化，
# 失效时 TwitterCrawler 从 x.com 的网页脚本中获取新的值并缓存，内置值不变时之后的运行直接使用
QUERY_IDS = {
    "UserByScreenName": "KybxDj9RrADIITXlGG8kpw",
    "UserTweets": "qJy3MbaNndtzxf9IqUzxMg",
    "Likes": "PgAssYGsPMMF1vVox5ysPg",
    "Bookmarks": "Glt3WAwBvNSPD-n_sqmX_A",
    "TweetDetail": "blErEeZkos5TDrWmrCp7cw",
}

API_DOMAIN = "https://x.com/i/api/graphql"


def graphql_endpoint(operation: str) -> str:
    """查询的内置接口地址，形如 {API_DOMAIN}/{queryId}/{查询名}"""
    return f"{API_DOMAIN}/{QUERY_IDS[operation]}/{operation}"


class TwitterAPIEndpoints:
    """
    API Endpoints for Twitter
    """

    # Twitter Domain
    TWITTER_DOMAIN = "https://x.com"

    API_DOMAIN = API_DOMAIN

    # User Detail
    USER_PROFILE = graphql_endpoint("UserByScreenName")

    # User Post
    USER_POST = graphql_endpoint("UserTweets")

    # User Like
    USER_LIKE = graphql_endpoint("Likes")

    # User Bookmark
    USER_BOOKMARK = graphql_endpoint("Bookmarks")

    # Post Detail
    POST_DETAIL = graphql_endpoint("TweetDetail")
