# path: f2/apps/twitter/api.py


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
