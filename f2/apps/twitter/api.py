# path: f2/apps/twitter/api.py


class TwitterAPIEndpoints:
    """
    API Endpoints for Twitter
    """

    # Twitter Domain
    TWITTER_DOMAIN = "https://x.com"

    API_DOMAIN = "https://x.com/i/api/graphql"

    # User Detail
    USER_PROFILE = f"{API_DOMAIN}/laYnJPCAcVo0o6pzcnlVxQ/UserByScreenName"

    # User Post
    USER_POST = f"{API_DOMAIN}/Tg82Ez_kxVaJf7OPbUdbCg/UserTweets"

    # User Like
    USER_LIKE = f"{API_DOMAIN}/px6_YxfWkXo0odY84iqqmw/Likes"

    # User Bookmark
    USER_BOOKMARK = f"{API_DOMAIN}/L7vvM2UluPgWOW4GDvWyvw/Bookmarks"

    # Post Detail
    POST_DETAIL = f"{API_DOMAIN}/nBS-WpgA6ZG0CyNHD517JQ/TweetDetail"
