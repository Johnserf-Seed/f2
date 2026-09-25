# path: f2/apps/twitter/filter.py

from typing import Any, List, Optional, Tuple

from f2.apps.twitter.utils import best_mp4_url, extract_desc, sort_mp4_urls
from f2.utils.json.filter import JSONModel, filter_to_list
from f2.utils.string.formatter import replaceT
from f2.utils.time.timestamp import timestamp_2_str

# Filter


class TweetDetailFilter(JSONModel):
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

    # 推文内容
    @property
    def tweet_desc(self):
        return replaceT(
            extract_desc(self._get_attr_value(f"{self._result_path}.legacy.full_text"))
        )

    @property
    def tweet_desc_raw(self):
        return extract_desc(
            self._get_attr_value(f"{self._result_path}.legacy.full_text")
        )

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
            f"{self._result_path}.core.user_results.result.profile_banner_url"
        )

    # 关注者
    @property
    def followers_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.followers_count"
        )

    # 正在关注
    @property
    def friends_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.friends_count"
        )

    # 帖子数（推文数&回复 maybe？）
    @property
    def statuses_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.statuses_count"
        )

    # 媒体数（图片数&视频数）
    @property
    def media_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.media_count"
        )

    # 喜欢数
    @property
    def favourites_count(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.favourites_count"
        )

    @property
    def has_custom_timelines(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.has_custom_timelines"
        )

    @property
    def location(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.location"
        )

    @property
    def can_dm(self):
        return self._get_attr_value(
            f"{self._result_path}.core.user_results.result.can_dm"
        )

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserProfileFilter(JSONModel):
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

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class PostTweetFilter(JSONModel):
    # 用户发布的推文__typename是TweetWithVisibilityResults
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
    @property
    def tweet_id(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.conversation_id_str"
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
        text_list = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.full_text"
        )

        if text_list is None:
            return []

        return [
            extract_desc(text) for text in text_list if text and isinstance(text, str)
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

    def _to_raw(self) -> dict:
        return self._data

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
    def __init__(self, data):
        super().__init__(data)


class BookmarkTweetFilter(JSONModel):
    # 用户发布的推文__typename是TweetWithVisibilityResults
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
    @property
    def tweet_id(self):
        return self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.conversation_id_str"
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
        text_list = self._get_list_attr_value(
            "$.data.bookmark_timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.full_text"
        )

        if text_list is None:
            return []

        return [
            extract_desc(text) for text in text_list if text and isinstance(text, str)
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

    def _to_raw(self) -> dict:
        return self._data

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
