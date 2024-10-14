# path: f2/apps/twitter/filter.py

from f2.utils.json_filter import JSONModel
from f2.utils.utils import timestamp_2_str, replaceT

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
    def tweet_created_time(self):
        return timestamp_2_str(
            self._get_attr_value(
                "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.created_at"
            )
        )

    # 推文内容
    @property
    def tweet_desc(self):
        return replaceT(
            self._get_attr_value(
                "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.full_text"
            ).split()[0]
        )

    @property
    def tweet_desc_raw(self):
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.full_text"
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
        return self._get_attr_value(
            "$.data.threaded_conversation_with_injections_v2.instructions[0].entries[0].content.itemContent.tweet_results.result.legacy.extended_entities.media[*].video_info.variants[*].url"
        )

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
    def nicename_raw(self):
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
    def min_cursor(self):
        return self._get_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[-2].content.value"
        )

    @property
    def max_cursor(self):
        return self._get_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[-1].content.value"
        )

    # tweet
    @property
    def tweet_id(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.conversation_id_str"
        )

    @property
    def tweet_created_at(self):
        create_times = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.created_at"
        )
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    @property
    def tweet_favorite_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.favorite_count"
        )

    @property
    def tweet_reply_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.reply_count"
        )

    @property
    def tweet_retweet_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.retweet_count"
        )

    @property
    def tweet_quote_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.quote_count"
        )

    @property
    def tweet_views_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.views.count"
        )

    @property
    def tweet_desc(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.full_text"
            )
        )

    @property
    def tweet_desc_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.full_text"
        )

    @property
    def tweet_media_status(self):
        # root = self._get_list_attr_value(
        #     "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities"
        # )
        # print(root, type(root))
        # if root[0].get("media", None) is None:
        #     return None

        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities.media[*].ext_media_availability.status"
        )

    @property
    def tweet_media_type(self):
        # root = self._get_list_attr_value(
        #     "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities"
        # )
        # if root[0].get("media", None) is None:
        #     return None

        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities.media[0].type"
        )

    @property
    def tweet_media_url(self):

        media_list = []
        # root = self._get_list_attr_value(
        #     "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities"
        # )
        # if root[0].get("media", None) is None:
        #     media_list.append(None)

        entries = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities.media[*]"
        )

        if entries is not None:
            for entry in entries:
                media_list.append(entry.get("media_url_https", None))
        return media_list

    @property
    def tweet_video_url(self):

        # [*].video_info.variants
        # return [
        #     (
        #         [
        #             video["url"]
        #             for video in video_url
        #             if "url" in video and video["url"]
        #         ]
        #         if video_url
        #         else None
        #     )
        #     for video_url in video_url_list
        # ]

        video_list = []
        # root = self._get_list_attr_value(
        #     "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities"
        # )
        # if root[0].get("media", None) is None:
        #     video_list.append(None)

        video_url_list = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities.media"
        )

        if video_url_list == []:
            return []

        if isinstance(video_url_list[0], dict):
            video_url_list = [video_url_list]

        for video_url in video_url_list:
            urls = []
            # 如果没有video_info字段，说明不是视频则为None
            # 例如 [[1,2,3],None,[1,2,3]]，None要与index对应
            # 如果有video_info字段，说明是视频，返回url列表
            # 例如 [[1,2,3],[1,2,3],[1,2,3]]
            for video in video_url:
                video_info = video.get("video_info")
                if video_info:
                    variants = video_info.get("variants")
                    for url in variants:
                        urls.append(url.get("url", None))
            video_list.append(urls if urls else None)
        return video_list

    @property
    def tweet_video_bitrate(self):
        biterate_list = []
        # root = self._get_list_attr_value(
        #     "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities"
        # )
        # if root[0].get("media", None) is None:
        #     biterate_list.append(None)

        biterate_url_list = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.legacy.entities.media[*].video_info.variants[*]"
        )

        if biterate_url_list == []:
            return []

        if isinstance(biterate_url_list[0], dict):
            biterate_url_list = [biterate_url_list]

        for biterate_url in biterate_url_list:
            urls = []
            for biterate in biterate_url:
                biterate_info = biterate.get("video_info")
                if biterate_info:
                    variants = biterate_info.get("variants")
                    for url in variants:
                        urls.append(url.get("biterate", None))
            biterate_list.append(urls if urls else None)
        return biterate_list

    # user
    @property
    def user_id(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.id"
        )

    @property
    def is_blue_verified(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.is_blue_verified"
        )

    @property
    def user_created_at(self):
        create_times = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.created_at"
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
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.description"
            )
        )

    @property
    def user_description_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.description"
        )

    @property
    def user_location(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.location"
        )

    @property
    def user_friends_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.friends_count"
        )

    @property
    def user_followers_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.followers_count"
        )

    @property
    def user_favourites_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.favourites_count"
        )

    @property
    def user_media_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.media_count"
        )

    @property
    def user_statuses_count(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.statuses_count"
        )

    @property
    def nickname(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.name"
            )
        )

    @property
    def nickname_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.name"
        )

    @property
    def user_screen_name(self):
        return replaceT(
            self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.screen_name"
            )
        )

    @property
    def user_screen_name_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.screen_name"
        )

    @property
    def user_profile_banner_url(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.tweet.core.user_results.result.legacy.profile_banner_url"
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
        exclude_list = [
            "max_cursor",
            "min_cursor",
        ]

        keys = [
            prop_name
            for prop_name in dir(self)
            if not prop_name.startswith("__")
            and not prop_name.startswith("_")
            and prop_name not in exclude_list
        ]

        tweet_entries = (
            self._get_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries"
            )
            or []
        )

        list_dicts = []
        for entry in tweet_entries:
            d = {
                "max_cursor": self.max_cursor,
                "min_cursor": self.min_cursor,
            }
            for key in keys:
                attr_values = getattr(self, key)
                index = tweet_entries.index(entry)
                d[key] = attr_values[index] if index < len(attr_values) else None
            list_dicts.append(d)
        return list_dicts

        # list_dicts = []
        # for index, (key, entry) in enumerate(tweet_entries.items()):
        #     d = {
        #         "max_cursor": self.max_cursor,
        #         "min_cursor": self.min_cursor,
        #     }
        #     for key in keys:
        #         attr_values = getattr(self, key)
        #         if attr_values is not None:
        #             d[key] = attr_values[index] if index < len(attr_values) else None
        #         else:
        #             d[key] = None
        #     list_dicts.append(d)
        # return list_dicts


class PostRetweetFilter(JSONModel):
    # 用户发布的推文__typename是TweetWithVisibilityResults
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
        return replaceT(
            self._get_list_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.full_text"
            )
        )

    @property
    def tweet_desc_raw(self):
        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.full_text"
        )

    @property
    def tweet_media_status(self):
        root = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities"
        )
        if root[0].get("media", None) is None:
            return []

        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[*].ext_media_availability.status"
        )

    @property
    def tweet_media_type(self):
        root = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities"
        )
        if root[0].get("media", None) is None:
            return []

        return self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[0].type"
        )

    @property
    def tweet_media_url(self):

        media_list = []
        root = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities"
        )

        if isinstance(root, dict):
            root = [root]

        entries = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[*]"
        )

        if entries is not None:
            for entry in entries:
                if "media" not in root[entries.index(entry)]:
                    # print("media not in root")
                    media_list.append(None)
                else:
                    # print("media in root")
                    media_list.append(entry.get("media_url_https", None))
            # print("media_list:", media_list)

        return media_list

    @property
    def tweet_video_url(self):

        video_list = []
        root = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities"
        )

        if isinstance(root, dict):
            root = [root]

        video_url_list = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[*]"
        )
        # print(
        #     "第一条推文==================================",
        #     video_url_list,
        #     type(video_url_list),
        # )

        # if video_url_list == []:
        #     return video_url_list

        # if isinstance(video_url_list[0], dict):
        #     video_url_list = [video_url_list]

        if video_url_list is not None:
            for video_dict in video_url_list:
                urls = []

                # # 将有media的下标与root对应
                # video_index = video_url_list.index(video_dict)
                # video_dict_list = root[video_index][
                #     "media"
                # ]  # list，其中的media可能[{0},{1},{2}]或者{0}

                # 如果没有video_info字段，说明不是视频则为None
                # 例如 [[1,2,3],None,[1,2,3]]，None要与index对应
                # 如果有video_info字段，说明是视频，返回url列表
                # 例如 [[1,2,3],[1,2,3],[1,2,3]]
                # print("----------------------------------")
                # print(root[video_url_list.index(video_dict)])
                # print("++++++++++++++++++++++++++++++++++")
                if "media" not in root[video_url_list.index(video_dict)]:
                    print(
                        "这个内容没有media",
                        root[video_url_list.index(video_dict)],
                        "下标",
                        video_url_list.index(video_dict),
                    )
                    print("++++++++++++++++++++++++++++++++++")
                    video_list.append(None)
                else:

                    video_dict_list = root[video_url_list.index(video_dict)][
                        "media"
                    ]  # list类型，其中的media可能[{0},{1},{2}]或者{0}

                    # print("有media内容类型", video_dict.get("type"))
                    # print(
                    #     "有media内容",
                    #     root[video_url_list.index(video_dict)],
                    #     "下标",
                    #     video_url_list.index(video_dict),
                    # )
                    # print(
                    #     video_dict.get("expanded_url"),
                    #     root[video_url_list.index(video_dict)]["media"][0][
                    #         "expanded_url"
                    #     ],
                    # )
                    # 视频类型的数据结构[[11],[11],[11,22,33]]
                    if video_dict_list[0].get("type") == "video":
                        for video_dict in video_dict_list:
                            # video_dict 为每一个视频字典
                            video_info = video_dict.get("video_info")
                            if video_info:
                                variants = video_info.get("variants")

                                # 只拿最后一个链接
                                # urls.append()
                                # for url in variants:
                                #     urls.append(url.get("url", None))
                                # print("视频链接", urls[-1])

                        video_list.append(urls if urls else None)
                    else:
                        print("有media内容类型是照片的", video_dict_list[0].get("type"))
                        print(
                            "这个media内容没有video",
                            video_dict_list,
                        )
                        print("++++++++++++++++++++++++++++++++++")
                        video_list.append(None)
        print("video_list==============", video_list)
        return video_list

    @property
    def tweet_video_bitrate(self):
        biterate_list = []
        root = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities"
        )
        # print("tweet_video_bitrate:", root[0].get("media", None))
        if root[0].get("media", None) is None:
            print(
                "============================tweet_video_bitrate:",
                root[0].get("media", None),
                "============================",
            )
            return []

        biterate_url_list = self._get_list_attr_value(
            "$.data.user.result.timeline_v2.timeline.instructions[-1].entries[*].content.itemContent.tweet_results.result.legacy.entities.media[*].video_info.variants[*]"
        )

        if biterate_url_list == []:
            return []

        if isinstance(biterate_url_list[0], dict):
            biterate_url_list = [biterate_url_list]

        for biterate_url in biterate_url_list:
            urls = []
            for biterate in biterate_url:
                biterate_info = biterate.get("video_info")
                if biterate_info:
                    variants = biterate_info.get("variants")
                    for url in variants:
                        urls.append(url.get("biterate", None))
            biterate_list.append(urls if urls else None)
        return biterate_list

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
        exclude_list = [
            "max_cursor",
            "min_cursor",
        ]

        keys = [
            prop_name
            for prop_name in dir(self)
            if not prop_name.startswith("__")
            and not prop_name.startswith("_")
            and prop_name not in exclude_list
        ]

        tweet_entries = (
            self._get_attr_value(
                "$.data.user.result.timeline_v2.timeline.instructions[-1].entries"
            )
            or []
        )

        list_dicts = []
        for entry in tweet_entries:
            d = {
                "max_cursor": self.max_cursor,
                "min_cursor": self.min_cursor,
            }
            for key in keys:
                attr_values = getattr(self, key)
                index = tweet_entries.index(entry)
                d[key] = attr_values[index] if index < len(attr_values) else None
            list_dicts.append(d)
        return list_dicts
