# path: f2/apps/twitter/api.py


class TwitterAPIEndpoints:
    """
    API Endpoints for Twitter
    """

    # Twitter Domain
    TWITTER_DOMAIN = "https://x.com"

    API_DOMAIN = "https://x.com/i/api/graphql"

    # Login
    LOGIN_ENDPOINT = f"{TWITTER_DOMAIN}/login/"

    # Home Timeline
    HOME_TIMELINE = f"{TWITTER_DOMAIN}/api/timeline/home.json"

    # User Timeline
    USER_TIMELINE = f"{TWITTER_DOMAIN}/api/timeline/user_timeline.json"

    # User Detail
    USER_PROFILE = f"{API_DOMAIN}/laYnJPCAcVo0o6pzcnlVxQ/UserByScreenName"

    # User Post
    USER_POST = f"{API_DOMAIN}/Tg82Ez_kxVaJf7OPbUdbCg/UserTweets"

    # User Like
    USER_LIKE = f"{TWITTER_DOMAIN}/api/favorite/item_list.json"

    # User Collect
    USER_COLLECT = f"{TWITTER_DOMAIN}/api/user/collect/item_list.json"

    # User Play List
    USER_PLAY_LIST = f"{TWITTER_DOMAIN}/api/user/playlist.json"

    # User Mix
    USER_MIX = f"{TWITTER_DOMAIN}/api/mix/item_list.json"

    # Guess You Like
    GUESS_YOU_LIKE = f"{TWITTER_DOMAIN}/api/related/item_list.json"

    # User Follow
    USER_FOLLOW = f"{TWITTER_DOMAIN}/api/relation/user/list.json"

    # User Fans
    USER_FANS = f"{TWITTER_DOMAIN}/api/relation/follower/list.json"

    # Post Detail
    POST_DETAIL = f"{API_DOMAIN}/nBS-WpgA6ZG0CyNHD517JQ/TweetDetail"

    # Post Comment
    POST_COMMENT = f"{TWITTER_DOMAIN}/api/comment/list.json"
