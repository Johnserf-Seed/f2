# path: f2/apps/twitter/filter.py

from typing import Any, Collection, List, Optional, Tuple

from f2.apps.twitter.utils import (
    best_mp4_url,
    extract_desc,
    media_items,
    sort_mp4_urls,
    tweet_created_at_to_timestamp,
    tweet_full_text,
)
from f2.utils.json.filter import JSONModel, filter_to_list
from f2.utils.string.formatter import replaceT
from f2.utils.time.timestamp import timestamp_2_str

# 网页端新版 GraphQL 接口（2026-10 实测）的用户对象不再有 legacy，字段拆到了 core、
# profile_bio 等处。键为 legacy 中的旧字段名，值为新结构中的位置
_USER_LEGACY_FIELDS = {
    "name": ("core", "name"),
    "screen_name": ("core", "screen_name"),
    "created_at": ("core", "created_at"),
    "description": ("profile_bio", "description"),
    "location": ("location", "location"),
    "url": ("website", "url"),
    "profile_banner_url": ("banner", "image_url"),
    "profile_image_url_https": ("avatar", "image_url"),
    "followers_count": ("relationship_counts", "followers"),
    "friends_count": ("relationship_counts", "following"),
    "statuses_count": ("tweet_counts", "tweets"),
    "media_count": ("tweet_counts", "media_tweets"),
    "favourites_count": ("action_counts", "favorites_count"),
    "pinned_tweet_ids_str": ("pinned_items", "tweet_ids_str"),
    "protected": ("privacy", "protected"),
    "verified": ("verification", "verified"),
}


def _backfill_user_legacy(user: dict) -> None:
    """按旧字段名把新版用户对象的字段补进 legacy，已有的字段不覆盖"""
    values = {
        field: user[group][key]
        for field, (group, key) in _USER_LEGACY_FIELDS.items()
        if isinstance(user.get(group), dict) and key in user[group]
    }
    if not values:
        return
    legacy = user.get("legacy")
    if not isinstance(legacy, dict):
        legacy = user["legacy"] = {}
    for field, value in values.items():
        legacy.setdefault(field, value)


def normalize_graphql_response(data: Any) -> Any:
    """
    把网页端 GraphQL 接口的响应整理成过滤器读取的结构，返回副本，不修改原数据
    (Normalize a GraphQL response into the structure the filters read)

    queryId 随 X 发版更换后，新的查询返回的结构也会变化，旧 queryId 仍返回旧结构：

    - 用户对象的字段从 legacy 移到了 core、profile_bio 等处：按旧字段名补回 legacy
    - 主页与喜欢的时间线由 timeline_v2 改名为 timeline：补上 timeline_v2
    - 受限推文包在 TweetWithVisibilityResults 里：直接取出其中的 tweet，
      此前时间线中的这类推文没有作者信息，被当成广告跳过

    Args:
        data (Any): 接口响应 (API response)

    Returns:
        Any: 整理后的响应 (Normalized response)
    """
    if isinstance(data, list):
        return [normalize_graphql_response(item) for item in data]
    if not isinstance(data, dict):
        return data

    node = {key: normalize_graphql_response(value) for key, value in data.items()}
    typename = node.get("__typename")
    if typename == "TweetWithVisibilityResults" and isinstance(node.get("tweet"), dict):
        return node["tweet"]
    if typename == "User":
        _backfill_user_legacy(node)
        if "timeline" in node and "timeline_v2" not in node:
            node["timeline_v2"] = node["timeline"]
    return node


def _tweet_items(entry: dict) -> List[dict]:
    """取出模块条目（如主页的串推）中的推文，按普通条目的结构返回"""
    tweets = []
    for item in (entry.get("content") or {}).get("items") or []:
        if not isinstance(item, dict):
            continue
        item_content = (item.get("item") or {}).get("itemContent") or {}
        if item_content.get("tweet_results"):
            tweets.append(
                {
                    "entryId": item.get("entryId"),
                    "content": {
                        "entryType": "TimelineTimelineItem",
                        "itemContent": item_content,
                    },
                }
            )
    return tweets


def merge_timeline_entries(timeline: Any) -> None:
    """
    把时间线中分散的推文条目合并到最后一条指令的 entries 中（原地修改）
    (Merge the scattered tweet entries of a timeline into the entries of the last instruction)

    过滤器只读取最后一条指令的 entries，以下推文此前都不会下载：

    - 置顶推文单独放在 TimelinePinEntry 指令里，不在推文列表中
    - 主页中的串推（自己回复自己）放在 profile-conversation 模块的 items 里

    合并时推文在前、游标在后，同一推文只保留一次；不含推文的模块（如推荐关注）保持原样。

    Args:
        timeline (Any): 时间线，即包含 instructions 的字典 (The timeline holding instructions)
    """
    if not isinstance(timeline, dict) or not isinstance(
        timeline.get("instructions"), list
    ):
        return

    instructions = [i for i in timeline["instructions"] if isinstance(i, dict)]
    pinned = [i["entry"] for i in instructions if isinstance(i.get("entry"), dict)]
    listed = [
        e
        for i in instructions
        if isinstance(i.get("entries"), list)
        for e in i["entries"]
        if isinstance(e, dict)
    ]
    if not pinned and not any(_tweet_items(e) for e in listed):
        return

    entries, cursors, seen = [], [], set()
    for entry in pinned + listed:
        content = entry.get("content") or {}
        if content.get("cursorType"):
            cursors.append(entry)
            continue
        for tweet in _tweet_items(entry) or [entry]:
            item_content = tweet["content"].get("itemContent") or {}
            result = (item_content.get("tweet_results") or {}).get("result") or {}
            tweet_id = result.get("rest_id") if isinstance(result, dict) else None
            if tweet_id in seen:
                continue
            if tweet_id:
                seen.add(tweet_id)
            entries.append(tweet)

    timeline["instructions"] = [
        i for i in instructions if "entries" not in i and "entry" not in i
    ] + [{"type": "TimelineAddEntries", "entries": entries + cursors}]


class _GraphQLFilter(JSONModel):
    """网页端 GraphQL 接口过滤器的基类：先整理响应结构再读取，_to_raw 仍返回原始响应"""

    def __init__(self, data: Any):
        super().__init__(normalize_graphql_response(data))
        self._raw = data

    def _to_raw(self) -> dict:
        return self._raw


def _entry_tweet_id(entry: Any) -> Optional[str]:
    """条目中推文的 ID，游标、推荐关注等不是推文的条目返回 None"""
    if not isinstance(entry, dict):
        return None
    item_content = (entry.get("content") or {}).get("itemContent") or {}
    result = (item_content.get("tweet_results") or {}).get("result") or {}
    legacy = result.get("legacy") if isinstance(result, dict) else None
    return legacy.get("id_str") if isinstance(legacy, dict) else None


class _TimelineFilter(_GraphQLFilter):
    """主页、喜欢与收藏等时间线过滤器的基类 (Base class of timeline filters)"""

    # 包含 instructions 的时间线所在的 JSONPath
    _TIMELINE = ""

    def __init__(self, data: Any):
        super().__init__(data)
        merge_timeline_entries(self._get_attr_value(self._TIMELINE))

    def _keep_tweets(self, tweet_ids: Collection[str]) -> Any:
        """
        返回只保留指定推文的新过滤器，游标等不是推文的条目保留
        (Return a new filter keeping only the given tweets; other entries are kept)

        接口不按 count 返回，日期区间与最大数量需要在一页之内截取。
        """
        page = type(self)(self._raw)
        timeline = page._get_attr_value(self._TIMELINE)
        if not isinstance(timeline, dict) or not timeline.get("instructions"):
            return page
        last = timeline["instructions"][-1]
        last["entries"] = [
            entry
            for entry in last["entries"]
            if _entry_tweet_id(entry) is None or _entry_tweet_id(entry) in tweet_ids
        ]
        return page


# Filter


class TweetDetailFilter(_GraphQLFilter):
    _INSTRUCTIONS = "$.data.threaded_conversation_with_injections_v2.instructions"

    def __init__(self, data: Any, tweet_id: Optional[str] = None):
        super().__init__(data)
        self._entry_path, self._result_path = self._locate_tweet(tweet_id)

    def _locate_tweet(self, tweet_id: Optional[str]) -> Tuple[str, str]:
        """
        找到目标推文所在的指令与条目，返回条目与推文数据的 JSONPath 前缀。

        接口会在 instructions 前面插入 TimelineClearCache 等不含推文的指令（#436），
        回复或评论的会话里 entries[0] 可能是上层推文（#234），所以不能写死下标。
        """
        try:
            instructions = self._data["data"][
                "threaded_conversation_with_injections_v2"
            ]["instructions"]
        except (KeyError, TypeError):
            instructions = []

        target = f"tweet-{tweet_id}" if tweet_id else None
        for i, instruction in enumerate(instructions):
            entries = (
                instruction.get("entries") if isinstance(instruction, dict) else None
            )
            if not entries:
                continue

            tweet_entries = [
                j
                for j, entry in enumerate(entries)
                if isinstance(entry, dict)
                and str(entry.get("entryId", "")).startswith("tweet-")
            ]
            index = next(
                (j for j in tweet_entries if entries[j].get("entryId") == target),
                tweet_entries[0] if tweet_entries else 0,
            )
            entry_path = f"{self._INSTRUCTIONS}[{i}].entries[{index}]"
            result_path = f"{entry_path}.content.itemContent.tweet_results.result"

            # 受限推文包在 TweetWithVisibilityResults 里，数据位于 result.tweet
            entry = entries[index] if isinstance(entries[index], dict) else {}
            item = (entry.get("content") or {}).get("itemContent") or {}
            result = (item.get("tweet_results") or {}).get("result") or {}
            if "legacy" not in result and isinstance(result.get("tweet"), dict):
                result_path += ".tweet"
            return entry_path, result_path

        entry_path = f"{self._INSTRUCTIONS}[0].entries[0]"
        return entry_path, f"{entry_path}.content.itemContent.tweet_results.result"

    # tweet
    @property
    def tweet_id(self):
        return self._get_attr_value(f"{self._result_path}.legacy.id_str")

    # tweet_id = property(
    #     lambda self: self._get_attr_value(
    #         "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.rest_id"
    #     )
    # )

    @property
    def tweet_type(self):
        return self._get_attr_value(f"{self._entry_path}.content.itemContent.itemType")

    @property
    def tweet_views_count(self):
        return self._get_attr_value(f"{self._result_path}.views.count")

    # 收藏数
    @property
    def tweet_bookmark_count(self):
        return self._get_attr_value(f"{self._result_path}.legacy.bookmark_count")

    # 点赞数
    @property
    def tweet_favorite_count(self):
        return self._get_attr_value(f"{self._result_path}.legacy.favorite_count")

    # 评论数
    @property
    def tweet_reply_count(self):
        return self._get_attr_value(f"{self._result_path}.legacy.reply_count")

    # 转推数
    @property
    def tweet_retweet_count(self):
        return self._get_attr_value(f"{self._result_path}.legacy.retweet_count")

    # 发布时间
    @property
    def tweet_created_at(self):
        created_at = self._get_attr_value(f"{self._result_path}.legacy.created_at")
        # 添加空值检查
        if created_at is None:
            return ""
        return timestamp_2_str(created_at)

    # 发布时间的秒级时间戳，按日期区间筛选时使用（tweet_created_at 按 UTC 时间格式化）
    @property
    def tweet_timestamp(self):
        return tweet_created_at_to_timestamp(
            self._get_attr_value(f"{self._result_path}.legacy.created_at")
        )

    # 推文内容
    @property
    def tweet_desc(self):
        return replaceT(
            extract_desc(self._get_attr_value(f"{self._result_path}.legacy.full_text"))
        )

    @property
    def tweet_desc_raw(self):
        # 完整文案（长推文、链接之后的内容都保留），用于 desc.txt
        return tweet_full_text(self._get_attr_value(self._result_path))

    # 媒体状态
    @property
    def tweet_media_status(self):
        return self._get_attr_value(
            f"{self._result_path}.legacy.entities.media[*].ext_media_availability.status"
        )

    # 媒体类型
    @property
    def tweet_media_type(self):
        return self._get_attr_value(
            f"{self._result_path}.legacy.entities.media[*].type"
        )

    # 图片链接
    @property
    def tweet_media_url(self):
        media_urls = self._get_attr_value(
            f"{self._result_path}.legacy.entities.media[*].media_url_https"
        )

        if media_urls is None:
            return []

        if not isinstance(media_urls, list):
            media_urls = [media_urls]
        return media_urls

    # 视频链接：只保留 MP4，按码率从低到高排列，下载时取最后一个（#436）
    @property
    def tweet_video_url(self):
        return sort_mp4_urls(
            self._get_attr_value(
                f"{self._result_path}.legacy.extended_entities.media[*].video_info.variants[*]"
            )
        )

    # 每个媒体的类型与下载链接：图文混合、多个视频的推文需要逐个下载
    @property
    def tweet_media(self):
        return media_items(
            self._get_attr_value(f"{self._result_path}.legacy.extended_entities.media")
            or self._get_attr_value(f"{self._result_path}.legacy.entities.media")
        )

    # 视频时长
    @property
    def tweet_video_duration(self):
        return self._get_attr_value(
            f"{self._result_path}.legacy.extended_entities.media[*].video_info.duration_millis"
        )

    # 视频码率
    @property
    def tweet_video_bitrate(self):
        return self._get_attr_value(
            f"{self._result_path}.legacy.extended_entities.media[*].video_info.variants[*].bitrate"
        )

    # User
    # 注册时间
    @property
    def join_time(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.created_at"
        )

    # 蓝V认证
    @property
    def is_blue_verified(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.is_blue_verified"
        )

    # 用户ID example: VXNlcjoxNDkzODI0MTA2Njk2OTAwNjEx
    @property
    def user_id(self):
        return self._get_attr_value(f"{self._result_path}.core.user_results.result.id")

    # 用户唯一ID（推特ID） example: Asai_chan_
    @property
    def user_unique_id(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.screen_name"
        )

    # 昵称 example: 核酸酱
    @property
    def nickname(self):
        return replaceT(
            self._get_attr_value(
                f"{self._result_path}.core.user_results.result.legacy.name"
            )
        )

    @property
    def nickname_raw(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.name"
        )

    @property
    def user_description(self):
        return replaceT(
            self._get_attr_value(
                f"{self._result_path}.core.user_results.result.legacy.description"
            )
        )

    @property
    def user_description_raw(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.description"
        )

    # 置顶推文ID
    @property
    def user_pined_tweet_id(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.pinned_tweet_ids_str[0]"
        )

    # 主页背景图片
    @property
    def user_profile_banner_url(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.profile_banner_url"
        )

    # 关注者
    @property
    def followers_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.followers_count"
        )

    # 正在关注
    @property
    def friends_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.friends_count"
        )

    # 帖子数（推文数&回复 maybe？）
    @property
    def statuses_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.statuses_count"
        )

    # 媒体数（图片数&视频数）
    @property
    def media_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.media_count"
        )

    # 喜欢数
    @property
    def favourites_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.favourites_count"
        )

    @property
    def has_custom_timelines(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.has_custom_timelines"
        )

    @property
    def location(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.location"
        )

    @property
    def can_dm(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.legacy.can_dm"
        )

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserProfileFilter(_GraphQLFilter):
    # User
    # 蓝V认证
    @property
    def is_blue_verified(self):
        return self._get_attr_value("$.data.user.result.is_blue_verified")

    # 用户ID example: VXNlcjoxNDkzODI0MTA2Njk2OTAwNjEx
    @property
    def user_id(self):
        return self._get_attr_value("$.data.user.result.id")

    # 获取主页需要这个rest_id
    @property
    def user_rest_id(self):
        return self._get_attr_value("$.data.user.result.rest_id")

    # 用户唯一ID（推特ID） example: Asai_chan_
    @property
    def user_unique_id(self):
        return self._get_attr_value("$.data.user.result.legacy.screen_name")

    # 注册时间
    @property
    def join_time(self):
        created_at = self._get_attr_value("$.data.user.result.legacy.created_at")
        # 添加空值检查
        if created_at is None:
            return ""
        return timestamp_2_str(created_at)

    # 昵称 example: 核酸酱
    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.data.user.result.legacy.name"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.data.user.result.legacy.name")

    @property
    def user_description(self):
        return replaceT(self._get_attr_value("$.data.user.result.legacy.description"))

    @property
    def user_description_raw(self):
        return self._get_attr_value("$.data.user.result.legacy.description")

    # 置顶推文ID
    @property
    def user_pined_tweet_id(self):
        return self._get_attr_value("$.data.user.result.legacy.pinned_tweet_ids_str[0]")

    # 主页背景图片
    @property
    def user_profile_banner_url(self):
        return self._get_attr_value("$.data.user.result.legacy.profile_banner_url")

    # 关注者
    @property
    def followers_count(self):
        return self._get_attr_value("$.data.user.result.legacy.followers_count")

    # 正在关注
    @property
    def friends_count(self):
        return self._get_attr_value("$.data.user.result.legacy.friends_count")

    # 帖子数（推文数&回复 maybe？）
    @property
    def statuses_count(self):
        return self._get_attr_value("$.data.user.result.legacy.statuses_count")

    # 媒体数（图片数&视频数）
    @property
    def media_count(self):
        return self._get_attr_value("$.data.user.result.legacy.media_count")

    # 喜欢数
    @property
    def favourites_count(self):
        return self._get_attr_value("$.data.user.result.legacy.favourites_count")

    @property
    def has_custom_timelines(self):
        return self._get_attr_value("$.data.user.result.legacy.has_custom_timelines")

    @property
    def location(self):
        return self._get_attr_value("$.data.user.result.legacy.location")

    @property
    def can_dm(self):
        return self._get_attr_value("$.data.user.result.legacy.can_dm")

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class PostTweetFilter(_TimelineFilter):
    _TIMELINE = "$.data.user.result.timeline_v2.timeline"

    @property
    def cursorType(self):
        return self._get_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[-1].content.cursorType"
        )

    @property
    def min_cursor(self):
        return self._get_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[-2].content.value"
        )

    @property
    def max_cursor(self):
        return self._get_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[-1].content.value"
        )

    @property
    def entryId(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].entryId"
        )

    # tweet
    # 推文自身的 ID。conversation_id_str 是所在会话根推文的 ID，喜欢或收藏的是回复时
    # 会取成别人的推文，同一会话的多条回复还会因此同名，后面的被当成已下载跳过
    @property
    def tweet_id(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.id_str"
        )

    @property
    def tweet_created_at(self):
        create_times = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.created_at"
        )
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    # 发布时间的秒级时间戳，按日期区间筛选时使用（tweet_created_at 按 UTC 时间格式化）
    @property
    def tweet_timestamp(self):
        return [
            tweet_created_at_to_timestamp(created_at)
            for created_at in self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.created_at"
            )
            or []
        ]

    # 置顶推文排在最前面，不受发布时间倒序的限制
    @property
    def tweet_pinned(self):
        return [
            context == "Pin"
            for context in self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.socialContext.contextType"
            )
            or []
        ]

    @property
    def tweet_favorite_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.favorite_count"
        )

    @property
    def tweet_reply_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.reply_count"
        )

    @property
    def tweet_retweet_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.retweet_count"
        )

    @property
    def tweet_quote_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.quote_count"
        )

    @property
    def tweet_views_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.views.count"
        )

    @property
    def tweet_desc(self):
        text_list = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.full_text"
        )

        if text_list is None:
            return []

        return replaceT(
            [
                extract_desc(text) if text and isinstance(text, str) else ""
                for text in text_list
            ]
        )

    @property
    def tweet_desc_raw(self):
        # 完整文案，用于 desc.txt。此前跳过没有文案的条目，列表变短，_to_list 按下标对齐时
        # 后面的推文都拿到了别的推文的文案
        return [
            tweet_full_text(result)
            for result in self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result"
            )
            or []
        ]

    @property
    def tweet_media_status(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[*].ext_media_availability.status"
        )

    @property
    def tweet_media_type(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[0].type"
        )

    @property
    def tweet_media_url(self):
        media_lists = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media"
        )

        if not media_lists:
            return []

        return [
            (
                [
                    media["media_url_https"]
                    for media in media_list
                    if isinstance(media, dict) and "media_url_https" in media
                ]
                if media_list
                else None
            )
            for media_list in media_lists
        ]

    @property
    def tweet_video_url(self):
        video_url_lists = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media"
        )

        if not video_url_lists:
            return []

        return [
            (
                [
                    url
                    for url in (
                        best_mp4_url(video_url["video_info"].get("variants"))
                        for video_url in video_url_list
                        if isinstance(video_url, dict) and "video_info" in video_url
                    )
                    if url
                ]
                if video_url_list
                else None
            )
            for video_url_list in video_url_lists
        ]

    # 每个媒体的类型与下载链接：图文混合、多个视频的推文需要逐个下载
    @property
    def tweet_media(self):
        extended = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.extended_entities.media"
        )
        basic = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media"
        )
        return [
            media_items(media or fallback)
            for media, fallback in zip(extended or [], basic or [])
        ]

    # user
    @property
    def user_id(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.id"
        )

    @property
    def is_blue_verified(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.is_blue_verified"
        )

    @property
    def user_created_at(self):
        create_times = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.created_at"
        )
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    @property
    def user_description(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.description"
            )
        )

    @property
    def user_description_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.description"
        )

    @property
    def user_location(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.location"
        )

    @property
    def user_friends_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.friends_count"
        )

    @property
    def user_followers_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.followers_count"
        )

    @property
    def user_favourites_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.favourites_count"
        )

    @property
    def user_media_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.media_count"
        )

    @property
    def user_statuses_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.statuses_count"
        )

    @property
    def nickname(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.name"
            )
        )

    @property
    def nickname_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.name"
        )

    # 用户唯一ID（推特ID），命名模板的 {uid} 读取这个字段（移植自 #442）
    @property
    def user_unique_id(self):
        return self.user_screen_name

    @property
    def user_screen_name(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.screen_name"
            )
        )

    @property
    def user_screen_name_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.screen_name"
        )

    @property
    def user_profile_banner_url(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.profile_banner_url"
        )

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields: List[str] = [
            "max_cursor",
            "min_cursor",
            "cursorType",
        ]

        extra_fields: List[str] = [
            "max_cursor",
            "min_cursor",
        ]

        list_dicts = filter_to_list(
            self,
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class LikeTweetFilter(PostTweetFilter):
    pass


class BookmarkTweetFilter(_TimelineFilter):
    _TIMELINE = "$.data.bookmark_timeline_v2.timeline"

    @property
    def cursorType(self):
        return self._get_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[-1].content.cursorType"
        )

    @property
    def min_cursor(self):
        return self._get_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[-2].content.value"
        )

    @property
    def max_cursor(self):
        return self._get_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[-1].content.value"
        )

    @property
    def entryId(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].entryId"
        )

    # tweet
    # 推文自身的 ID。conversation_id_str 是所在会话根推文的 ID，喜欢或收藏的是回复时
    # 会取成别人的推文，同一会话的多条回复还会因此同名，后面的被当成已下载跳过
    @property
    def tweet_id(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.id_str"
        )

    @property
    def tweet_created_at(self):
        create_times = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.created_at"
        )
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    # 发布时间的秒级时间戳，按日期区间筛选时使用（tweet_created_at 按 UTC 时间格式化）
    @property
    def tweet_timestamp(self):
        return [
            tweet_created_at_to_timestamp(created_at)
            for created_at in self._get_list_attr_value(
                "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.created_at"
            )
            or []
        ]

    @property
    def tweet_favorite_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.favorite_count"
        )

    @property
    def tweet_reply_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.reply_count"
        )

    @property
    def tweet_retweet_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.retweet_count"
        )

    @property
    def tweet_quote_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.quote_count"
        )

    @property
    def tweet_views_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.views.count"
        )

    @property
    def tweet_desc(self):
        text_list = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.full_text"
        )

        if text_list is None:
            return []

        return replaceT(
            [
                extract_desc(text) if text and isinstance(text, str) else ""
                for text in text_list
            ]
        )

    @property
    def tweet_desc_raw(self):
        # 完整文案，用于 desc.txt。此前跳过没有文案的条目，列表变短，_to_list 按下标对齐时
        # 后面的推文都拿到了别的推文的文案
        return [
            tweet_full_text(result)
            for result in self._get_list_attr_value(
                "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result"
            )
            or []
        ]

    @property
    def tweet_media_status(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[*].ext_media_availability.status"
        )

    @property
    def tweet_media_type(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[0].type"
        )

    @property
    def tweet_media_url(self):
        media_lists = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media"
        )

        if media_lists is None:
            return []

        return [
            (
                [
                    media["media_url_https"]
                    for media in media_list
                    if isinstance(media, dict) and "media_url_https" in media
                ]
                if media_list
                else None
            )
            for media_list in media_lists
        ]

    @property
    def tweet_video_url(self):
        video_url_lists = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media"
        )

        if not video_url_lists:
            return []

        return [
            (
                [
                    url
                    for url in (
                        best_mp4_url(video_url["video_info"].get("variants"))
                        for video_url in video_url_list
                        if isinstance(video_url, dict) and "video_info" in video_url
                    )
                    if url
                ]
                if video_url_list
                else None
            )
            for video_url_list in video_url_lists
        ]

    # 每个媒体的类型与下载链接：图文混合、多个视频的推文需要逐个下载
    @property
    def tweet_media(self):
        extended = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.extended_entities.media"
        )
        basic = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media"
        )
        return [
            media_items(media or fallback)
            for media, fallback in zip(extended or [], basic or [])
        ]

    # user
    @property
    def user_id(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.id"
        )

    @property
    def is_blue_verified(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.is_blue_verified"
        )

    @property
    def user_created_at(self):
        create_times = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.created_at"
        )
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    @property
    def user_description(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.description"
            )
        )

    @property
    def user_description_raw(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.description"
        )

    @property
    def user_location(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.location"
        )

    @property
    def user_friends_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.friends_count"
        )

    @property
    def user_followers_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.followers_count"
        )

    @property
    def user_favourites_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.favourites_count"
        )

    @property
    def user_media_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.media_count"
        )

    @property
    def user_statuses_count(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.statuses_count"
        )

    @property
    def nickname(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.name"
            )
        )

    @property
    def nickname_raw(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.name"
        )

    # 用户唯一ID（推特ID），命名模板的 {uid} 读取这个字段（移植自 #442）
    @property
    def user_unique_id(self):
        return self.user_screen_name

    @property
    def user_screen_name(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.screen_name"
            )
        )

    @property
    def user_screen_name_raw(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.screen_name"
        )

    @property
    def user_profile_banner_url(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.core.user_results.result.legacy.profile_banner_url"
        )

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields: List[str] = [
            "max_cursor",
            "min_cursor",
            "cursorType",
        ]

        extra_fields: List[str] = [
            "max_cursor",
            "min_cursor",
        ]

        list_dicts = filter_to_list(
            self,
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries",
            exclude_fields,
            extra_fields,
        )

        return list_dicts
