# path: tests/test_twitter_graphql_schema.py

import copy

import pytest

from f2.apps.twitter.filter import (
    BookmarkTweetFilter,
    LikeTweetFilter,
    PostTweetFilter,
    TweetDetailFilter,
    UserProfileFilter,
    normalize_graphql_response,
)

CURSORS = [
    {"entryId": "cursor-top-1", "content": {"cursorType": "Top", "value": "TOP"}},
    {"entryId": "cursor-bottom-1", "content": {"cursorType": "Bottom", "value": "BOT"}},
]


def new_user(screen_name, name):
    """新版 queryId 返回的用户对象：没有 legacy，字段分散在 core、profile_bio 等处"""
    return {
        "__typename": "User",
        "id": f"VXNlcjo{screen_name}",
        "rest_id": "11348282",
        "core": {
            "created_at": "Wed Dec 19 20:20:32 +0000 2007",
            "name": name,
            "screen_name": screen_name,
        },
        "profile_bio": {"description": "简介"},
        "location": {"location": "Pale Blue Dot"},
        "banner": {"image_url": "https://pbs.twimg.com/profile_banners/1/2"},
        "relationship_counts": {"followers": 100, "following": 5},
        "tweet_counts": {"tweets": 70, "media_tweets": 20},
        "action_counts": {"favorites_count": 3},
        "pinned_items": {"tweet_ids_str": ["999"]},
    }


def tweet(tweet_id, user):
    return {
        "__typename": "Tweet",
        "rest_id": tweet_id,
        "core": {"user_results": {"result": user}},
        "legacy": {
            "id_str": tweet_id,
            "conversation_id_str": tweet_id,
            "full_text": "推文",
            "created_at": "Wed Oct 01 16:36:07 +0000 2026",
        },
    }


def entry(tweet_id, result):
    item = {"itemType": "TimelineTweet", "tweet_results": {"result": result}}
    return {"entryId": f"tweet-{tweet_id}", "content": {"itemContent": item}}


def user_timeline(entries, key="timeline"):
    instructions = [{"type": "TimelineAddEntries", "entries": entries + CURSORS}]
    timeline = {key: {"timeline": {"instructions": instructions}}}
    return {"data": {"user": {"result": {"__typename": "User", **timeline}}}}


def test_profile_reads_user_without_legacy():
    profile = UserProfileFilter(
        {"data": {"user": {"result": new_user("NASA", "美国宇航局")}}}
    )

    assert profile.nickname == "美国宇航局"
    assert profile.user_unique_id == "NASA"
    assert profile.user_rest_id == "11348282"
    assert profile.join_time == "2007-12-19 20-20-32"
    assert profile.user_description == "简介"
    assert profile.location == "Pale Blue Dot"
    assert profile.followers_count == 100
    assert profile.friends_count == 5
    assert profile.statuses_count == 70
    assert profile.media_count == 20
    assert profile.favourites_count == 3
    assert profile.user_pined_tweet_id == "999"


@pytest.mark.parametrize("filter_cls", [PostTweetFilter, LikeTweetFilter])
def test_timeline_renamed_from_timeline_v2(filter_cls):
    # 新版 queryId 的主页与喜欢列表把 timeline_v2 改名为 timeline，作者信息也没有 legacy
    data = user_timeline([entry("1", tweet("1", new_user("alice", "爱丽丝")))])

    page = filter_cls(data)
    items = page._to_list()

    assert page.max_cursor == "BOT"
    assert page.cursorType == "Bottom"
    assert [item["tweet_id"] for item in items] == ["1", None, None]
    assert items[0]["user_unique_id"] == "alice"
    assert items[0]["nickname"] == "爱丽丝"
    assert items[0]["user_id"] == "VXNlcjoalice"


def test_old_timeline_v2_still_works():
    data = user_timeline(
        [entry("1", tweet("1", new_user("bob", "鲍勃")))], "timeline_v2"
    )

    assert PostTweetFilter(data)._to_list()[0]["user_unique_id"] == "bob"


def test_restricted_tweet_in_timeline_is_not_skipped():
    # 包在 TweetWithVisibilityResults 里的推文此前没有作者信息，被下载器当成广告跳过
    wrapped = {
        "__typename": "TweetWithVisibilityResults",
        "tweet": tweet("2", new_user("carol", "卡罗尔")),
    }
    item = PostTweetFilter(user_timeline([entry("2", wrapped)]))._to_list()[0]

    assert item["tweet_id"] == "2"
    assert item["user_id"] == "VXNlcjocarol"
    assert item["tweet_desc"] == "推文"


def test_bookmark_reads_new_author_fields():
    entries = [entry("3", tweet("3", new_user("dave", "戴夫")))] + CURSORS
    data = {
        "data": {
            "bookmark_timeline_v2": {
                "timeline": {"instructions": [{"entries": entries}]}
            }
        }
    }

    item = BookmarkTweetFilter(data)._to_list()[0]

    assert (item["user_unique_id"], item["nickname"]) == ("dave", "戴夫")


def test_detail_reads_new_author_fields():
    data = {
        "data": {
            "threaded_conversation_with_injections_v2": {
                "instructions": [
                    {
                        "type": "TimelineAddEntries",
                        "entries": [entry("4", tweet("4", new_user("erin", "艾琳")))],
                    }
                ]
            }
        }
    }

    detail = TweetDetailFilter(data, "4")

    assert detail.user_unique_id == "erin"
    assert detail.nickname == "艾琳"
    # 此前作者的这些字段少了 legacy 一级，始终为空；新结构下 location 还会取到整个对象
    assert detail.followers_count == 100
    assert detail.location == "Pale Blue Dot"
    assert detail.user_profile_banner_url == "https://pbs.twimg.com/profile_banners/1/2"


def test_raw_response_is_left_unchanged():
    data = {"data": {"user": {"result": new_user("NASA", "NASA")}}}
    original = copy.deepcopy(data)

    profile = UserProfileFilter(data)

    assert profile.nickname == "NASA"
    assert data == original
    assert profile._to_raw() is data


def test_existing_legacy_fields_are_kept():
    user = new_user("NASA", "新名字")
    user["legacy"] = {"name": "旧名字"}

    normalized = normalize_graphql_response(user)

    assert normalized["legacy"]["name"] == "旧名字"
    assert normalized["legacy"]["screen_name"] == "NASA"


# ---------------- 置顶推文与主页串推 ----------------


def module(entry_id, items):
    return {
        "entryId": entry_id,
        "content": {"entryType": "TimelineTimelineModule", "items": items},
    }


def module_tweet(tweet_id, user):
    item = {
        "itemType": "TimelineTweet",
        "tweet_results": {"result": tweet(tweet_id, user)},
    }
    return {"entryId": f"m-tweet-{tweet_id}", "item": {"itemContent": item}}


def test_pinned_tweet_and_self_thread_are_downloaded():
    # 置顶推文在 TimelinePinEntry 里，串推在 profile-conversation 模块里，此前都不会下载
    user = new_user("nasa", "NASA")
    recommend = {
        "entryId": "u-1",
        "item": {"itemContent": {"itemType": "TimelineUser"}},
    }
    data = user_timeline(
        [
            entry("10", tweet("10", user)),
            module("who-to-follow-1", [recommend]),
            module(
                "profile-conversation-1",
                [module_tweet("11", user), module_tweet("12", user)],
            ),
        ]
    )
    instructions = data["data"]["user"]["result"]["timeline"]["timeline"][
        "instructions"
    ]
    instructions[:0] = [
        {"type": "TimelineClearCache"},
        {"type": "TimelinePinEntry", "entry": entry("9", tweet("9", user))},
    ]

    page = PostTweetFilter(data)
    items = page._to_list()

    assert [item["tweet_id"] for item in items] == [
        "9",
        "10",
        None,
        "11",
        "12",
        None,
        None,
    ]
    assert page.max_cursor == "BOT"
    assert page.min_cursor == "TOP"
    assert page.cursorType == "Bottom"


def test_pinned_tweet_listed_again_is_kept_once():
    user = new_user("nasa", "NASA")
    data = user_timeline([entry("9", tweet("9", user)), entry("10", tweet("10", user))])
    instructions = data["data"]["user"]["result"]["timeline"]["timeline"][
        "instructions"
    ]
    instructions.insert(
        0, {"type": "TimelinePinEntry", "entry": entry("9", tweet("9", user))}
    )

    items = PostTweetFilter(data)._to_list()

    assert [item["tweet_id"] for item in items] == ["9", "10", None, None]


def test_last_page_still_ends_paging():
    # 到底时只剩两个游标，handler 据此结束翻页
    page = LikeTweetFilter(user_timeline([]))

    assert page.cursorType == "Bottom"
    assert len(page.entryId) == 2
