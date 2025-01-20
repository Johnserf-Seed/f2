# path: f2/apps/twitter/filter.py

from f2.utils.json_filter import JSONModel
from f2.utils.utils import timestamp_2_str, replaceT, filter_to_list
from f2.apps.twitter.utils import extract_desc


# Filter


class TweetDetailFilter(JSONModel):
    # tweet
    @property
    def tweet_id(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.id_str"
        )

    # tweet_id = property(
    #     lambda self: self._get_attr_value(
    #         "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.rest_id"
    #     )
    # )

    @property
    def tweet_type(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.itemType"
        )

    @property
    def tweet_views_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.views.count"
        )

    # 收藏数
    @property
    def tweet_bookmark_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.bookmark_count"
        )

    # 点赞数
    @property
    def tweet_favorite_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.favorite_count"
        )

    # 评论数
    @property
    def tweet_reply_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.reply_count"
        )

    # 转推数
    @property
    def tweet_retweet_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.retweet_count"
        )

    # 发布时间
    @property
    def tweet_created_at(self):
        return timestamp_2_str(
            self._get_attr_value(
                "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.created_at"
            )
        )

    # 推文内容
    @property
    def tweet_desc(self):
        return replaceT(
            extract_desc(
                self._get_attr_value(
                    "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.full_text"
                )
            )
        )

    @property
    def tweet_desc_raw(self):
        return extract_desc(
            self._get_attr_value(
                "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.full_text"
            )
        )

    # 媒体状态
    @property
    def tweet_media_status(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.entities.media[*].ext_media_availability.status"
        )

    # 媒体类型
    @property
    def tweet_media_type(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.entities.media[*].type"
        )

    # 图片链接
    @property
    def tweet_media_url(self):
        media_urls = self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.entities.media[*].media_url_https"
        )
        if not isinstance(media_urls, list):
            media_urls = [media_urls]
        return media_urls

    # 视频链接（清晰度依次提高）
    @property
    def tweet_video_url(self):
        all_urls = self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.extended_entities.media[*].video_info.variants[*].url"
        )
        # 剔除包含 `.m3u8` 的链接
        return [url for url in all_urls if ".m3u8" not in url]

    # 视频时长
    @property
    def tweet_video_duration(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.extended_entities.media[*].video_info.duration_millis"
        )

    # 视频码率
    @property
    def tweet_video_bitrate(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.extended_entities.media[*].video_info.variants[*].bitrate"
        )

    # User
    # 注册时间
    @property
    def join_time(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.legacy.created_at"
        )

    # 蓝V认证
    @property
    def is_blue_verified(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.is_blue_verified"
        )

    # 用户ID example: VXNlcjoxNDkzODI0MTA2Njk2OTAwNjEx
    @property
    def user_id(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.id"
        )

    # 用户唯一ID（推特ID） example: Asai_chan_
    @property
    def user_unique_id(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.legacy.screen_name"
        )

    # 昵称 example: 核酸酱
    @property
    def nickname(self):
        return replaceT(
            self._get_attr_value(
                "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.legacy.name"
            )
        )

    @property
    def nickname_raw(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.legacy.name"
        )

    @property
    def user_description(self):
        return replaceT(
            self._get_attr_value(
                "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.legacy.description"
            )
        )

    @property
    def user_description_raw(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.legacy.description"
        )

    # 置顶推文ID
    @property
    def user_pined_tweet_id(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.legacy.pinned_tweet_ids_str[0]"
        )

    # 主页背景图片
    @property
    def user_profile_banner_url(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.profile_banner_url"
        )

    # 关注者
    @property
    def followers_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.followers_count"
        )

    # 正在关注
    @property
    def friends_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.friends_count"
        )

    # 帖子数（推文数&回复 maybe？）
    @property
    def statuses_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.statuses_count"
        )

    # 媒体数（图片数&视频数）
    @property
    def media_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.media_count"
        )

    # 喜欢数
    @property
    def favourites_count(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.favourites_count"
        )

    @property
    def has_custom_timelines(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.has_custom_timelines"
        )

    @property
    def location(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.location"
        )

    @property
    def can_dm(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.core.user_results.result.can_dm"
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
        return timestamp_2_str(
            self._get_attr_value("$.data.user.result.legacy.created_at")
        )

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

        return [
            (
                [
                    video_url["video_info"]["variants"][-1]["url"]
                    for video_url in video_url_list
                    if isinstance(video_url, dict) and "video_info" in video_url
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
        exclude_fields = [
            "max_cursor",
            "min_cursor",
            "cursorType",
        ]

        extra_fields = [
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

        return [
            (
                [
                    video_url["video_info"]["variants"][-1]["url"]
                    for video_url in video_url_list
                    if isinstance(video_url, dict) and "video_info" in video_url
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
        exclude_fields = [
            "max_cursor",
            "min_cursor",
            "cursorType",
        ]

        extra_fields = [
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
