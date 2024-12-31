# path: f2/apps/douyin/filter.py

from typing import List, Dict, Any
from f2.utils.json_filter import JSONModel
from f2.utils.utils import timestamp_2_str, replaceT, filter_to_list

# Filter


class UserProfileFilter(JSONModel):
    @property
    def avatar_url(self):
        return self._get_attr_value("$.user.avatar_larger.url_list[0]")

    @property
    def aweme_count(self):
        return self._get_attr_value("$.user.aweme_count")

    @property
    def city(self):
        return self._get_attr_value("$.user.city")

    @property
    def country(self):
        return self._get_attr_value("$.user.country")

    @property
    def favoriting_count(self):
        return self._get_attr_value("$.user.favoriting_count")

    @property
    def follower_count(self):
        return self._get_attr_value("$.user.follower_count")

    @property
    def following_count(self):
        return self._get_attr_value("$.user.following_count")

    @property
    def gender(self):
        return self._get_attr_value("$.user.gender")

    @property
    def ip_location(self):
        return self._get_attr_value("$.user.ip_location")

    @property
    def is_ban(self):
        return self._get_attr_value("$.user.is_ban")

    @property
    def is_block(self):
        return self._get_attr_value("$.user.is_block")

    @property
    def is_blocked(self):
        return self._get_attr_value("$.user.is_blocked")

    @property
    def is_star(self):
        return self._get_attr_value("$.user.is_star")

    @property
    def live_status(self):
        return self._get_attr_value("$.user.live_status")

    @property
    def mix_count(self):
        return self._get_attr_value("$.user.mix_count")

    @property
    def mplatform_followers_count(self):
        return self._get_attr_value("$.user.mplatform_followers_count")

    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.user.nickname"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.user.nickname")

    @property
    def room_id(self):
        return self._get_attr_value("$.user.room_id")

    @property
    def school_name(self):
        return self._get_attr_value("$.user.school_name")

    @property
    def sec_user_id(self):
        return self._get_attr_value("$.user.sec_uid")

    @property
    def short_id(self):
        return self._get_attr_value("$.user.short_id")

    @property
    def signature(self):
        return replaceT(self._get_attr_value("$.user.signature"))

    @property
    def signature_raw(self):
        return self._get_attr_value("$.user.signature")

    @property
    def total_favorited(self):
        return self._get_attr_value("$.user.total_favorited")

    @property
    def uid(self):
        return self._get_attr_value("$.user.uid")

    @property
    def unique_id(self):
        return self._get_attr_value("$.user.unique_id")

    @property
    def user_age(self):
        return self._get_attr_value("$.user.user_age")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserPostFilter(JSONModel):

    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def has_aweme(self) -> bool:
        return bool(
            self._get_attr_value("$.aweme_list")
        )  # 如果aweme_list是空的或None，此属性返回False

    @property
    def locate_item_cursor(self):
        return self._get_attr_value("$.locate_item_cursor")  # 定位作品用

    @property
    def aweme_id(self):
        ids = self._get_list_attr_value("$.aweme_list[*].aweme_id")
        return ids if isinstance(ids, list) else [ids]

    @property
    def aweme_type(self):
        return self._get_list_attr_value("$.aweme_list[*].aweme_type")

    @property
    def create_time(self):
        create_times = self._get_list_attr_value("$.aweme_list[*].create_time")
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    @property
    def desc(self):
        return replaceT(self._get_list_attr_value("$.aweme_list[*].desc"))

    @property
    def desc_raw(self):
        return self._get_list_attr_value("$.aweme_list[*].desc")

    @property
    def uid(self):
        return self._get_list_attr_value("$.aweme_list[*].author.uid")

    @property
    def sec_user_id(self):
        return self._get_list_attr_value("$.aweme_list[*].author.sec_uid")

    @property
    def nickname(self):
        return replaceT(self._get_list_attr_value("$.aweme_list[*].author.nickname"))

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.aweme_list[*].author.nickname")

    @property
    def author_avatar_thumb(self):
        return self._get_list_attr_value(
            "$.aweme_list[*].author.avatar_thumb.url_list[0]"
        )

    @property
    def images(self):
        images_list = self._get_list_attr_value("$.aweme_list[*].images")

        return [
            (
                [
                    img["url_list"][0]
                    for img in images
                    if isinstance(img, dict) and "url_list" in img and img["url_list"]
                ]
                if images
                else None
            )
            for images in images_list
        ]

    @property
    def images_video(self):
        images_video_list = self._get_list_attr_value("$.aweme_list[*].images")

        return [
            (
                [
                    live["video"]["play_addr"]["url_list"][0]
                    for live in images_video
                    if isinstance(live, dict) and live.get("video") is not None
                ]
                if images_video
                else []
            )
            for images_video in images_video_list
        ]

    @property
    def animated_cover(self):
        # 临时办法
        # https://github.com/h2non/jsonpath-ng/issues/82

        # 获取所有视频
        videos = self._get_list_attr_value("$.aweme_list[*].video")

        # 逐个视频判断是否存在animated_cover
        animated_covers = [
            (
                video.get("animated_cover", {}).get("url_list", [None])[0]
                if video.get("animated_cover")
                else None
            )
            for video in videos
        ]

        return animated_covers

    @property
    def cover(self):
        return self._get_list_attr_value(
            "$.aweme_list[*].video.origin_cover.url_list[0]"
        )

    @property
    def video_play_addr(self):
        return self._get_list_attr_value(
            "$.aweme_list[*].video.bit_rate[0].play_addr.url_list"
        )

    @property
    def video_bit_rate(self):
        bit_rate_data = self._get_list_attr_value("$.aweme_list[*].video.bit_rate")

        def extract_bit_rate(aweme):
            if not aweme:
                return []

            if isinstance(aweme, dict):
                return [aweme.get("bit_rate", 0)]

            if isinstance(aweme, list):
                return [item.get("bit_rate", 0) for item in aweme]

            return []

        return [extract_bit_rate(aweme) for aweme in bit_rate_data]

    @property
    def video_duration(self):
        return self._get_list_attr_value("$.aweme_list[*].video.duration")

    @property
    def part_see(self):
        return self._get_list_attr_value("$.aweme_list[*].status.part_see")

    @property
    def private_status(self):
        return self._get_list_attr_value("$.aweme_list[*].status.private_status")

    @property
    def is_prohibited(self):
        # true 代表视频侵权 false代表视频未侵权
        return self._get_list_attr_value("$.aweme_list[*].status.is_prohibited")

    @property
    def author_deleted(self):
        # true 代表作者删除 false 代表作者未删除
        return self._get_list_attr_value("$.aweme_list[*].music.author_deleted")

    @property
    def music_status(self):
        # 1 代表正常 0 代表异常
        return self._get_list_attr_value("$.aweme_list[*].music.status")

    @property
    def music_title(self):
        return replaceT(self._get_list_attr_value("$.aweme_list[*].music.title"))

    @property
    def music_title_raw(self):
        return self._get_list_attr_value("$.aweme_list[*].music.title")

    @property
    def music_play_url(self):
        return self._get_list_attr_value("$.aweme_list[*].music.play_url.url_list[0]")

    @property
    def has_more(self) -> bool:
        return bool(self._get_attr_value("$.has_more"))

    @property
    def max_cursor(self):
        return self._get_attr_value("$.max_cursor")

    @property
    def min_cursor(self):
        return self._get_attr_value("$.min_cursor")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields = [
            "status_code",
            "has_more",
            "max_cursor",
            "min_cursor",
            "has_aweme",
            "locate_item_cursor",
        ]

        extra_fields = [
            "status_code",
            "has_more",
            "max_cursor",
            "min_cursor",
        ]

        list_dicts = filter_to_list(
            self,
            "$.aweme_list",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class UserCollectionFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)

    @property
    def max_cursor(self):
        return self._get_attr_value("$.cursor")


class UserCollectsFilter(JSONModel):

    @property
    def max_cursor(self):
        return self._get_attr_value("$.cursor")

    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def collects_total_number(self):
        return self._get_attr_value("$.total_number")

    @property
    def has_more(self):
        return bool(self._get_attr_value("$.has_more"))

    @property
    def app_id(self):
        return self._get_list_attr_value("$.collects_list[*].app_id")

    @property
    def collects_cover(self):
        return self._get_list_attr_value(
            "$.collects_list[*].collects_cover.url_list[0]"
        )

    @property
    def collects_id(self):
        return self._get_list_attr_value("$.collects_list[*].collects_id")

    @property
    def collects_name(self):
        return replaceT(self._get_list_attr_value("$.collects_list[*].collects_name"))

    @property
    def collects_name_raw(self):
        return self._get_list_attr_value("$.collects_list[*].collects_name")

    @property
    def create_time(self):
        create_times = self._get_list_attr_value("$.collects_list[*].create_time")
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    @property
    def follow_status(self):
        return self._get_list_attr_value("$.collects_list[*].follow_status")

    @property
    def followed_count(self):
        return self._get_list_attr_value("$.collects_list[*].followed_count")

    @property
    def is_normal_status(self):
        return self._get_list_attr_value("$.collects_list[*].is_normal_status")

    @property
    def item_type(self):
        return self._get_list_attr_value("$.collects_list[*].item_type")

    @property
    def last_collect_time(self):
        create_times = self._get_list_attr_value("$.collects_list[*].last_collect_time")
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    @property
    def play_count(self):
        return self._get_list_attr_value("$.collects_list[*].play_count")

    @property
    def states(self):
        return self._get_list_attr_value("$.collects_list[*].states")

    @property
    def status(self):
        return self._get_list_attr_value("$.collects_list[*].status")

    @property
    def system_type(self):
        return self._get_list_attr_value("$.collects_list[*].system_type")

    @property
    def total_number(self):
        return self._get_list_attr_value("$.collects_list[*].total_number")

    @property
    def user_id(self):
        return self._get_list_attr_value("$.collects_list[*].user_id")

    # user_info
    @property
    def nickname(self):
        return replaceT(
            self._get_list_attr_value("$.collects_list[*].user_info.nickname")
        )

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.collects_list[*].user_info.nickname")

    @property
    def uid(self):
        return self._get_list_attr_value("$.collects_list[*].user_info.uid")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserMusicCollectionFilter(JSONModel):

    @property
    def max_cursor(self):
        return self._get_attr_value("$.cursor")

    @property
    def has_more(self):
        return self._get_attr_value("$.has_more")

    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def msg(self):
        return self._get_attr_value("$.msg")

    @property
    def album(self):
        return self._get_list_attr_value("$.mc_list[*].album")

    @property
    def audition_duration(self):
        return self._get_list_attr_value("$.mc_list[*].audition_duration")

    @property
    def duration(self):
        return self._get_list_attr_value("$.mc_list[*].duration")

    @property
    def author(self):
        return replaceT(self._get_list_attr_value("$.mc_list[*].author"))

    @property
    def author_raw(self):
        return self._get_list_attr_value("$.mc_list[*].author")

    @property
    def collect_status(self):
        return self._get_list_attr_value("$.mc_list[*].collect_stat")

    @property
    def music_status(self):
        return self._get_list_attr_value("$.mc_list[*].music_status")

    @property
    def cover_hd(self):
        return self._get_list_attr_value("$.mc_list[*].cover_hd.url_list[0]")

    @property
    def music_id(self):
        return self._get_list_attr_value("$.mc_list[*].id")

    @property
    def mid(self):
        return self._get_list_attr_value("$.mc_list[*].mid")

    @property
    def is_commerce_music(self):
        return self._get_list_attr_value("$.mc_list[*].is_commerce_music")

    @property
    def is_original(self):
        return self._get_list_attr_value("$.mc_list[*].is_original")

    @property
    def is_original_sound(self):
        return self._get_list_attr_value("$.mc_list[*].is_original_sound")

    @property
    def lyric_type(self):
        return self._get_list_attr_value("$.mc_list[*].lyric_type")

    @property
    def lyric_url(self):
        # 不是每个作品都有 lyric_url，如果不存在则为 None
        lyric_urls = []
        for item in self._data.get("mc_list"):
            lyric_urls.append(item.get("lyric_url", None))

        return lyric_urls

    @property
    def play_url(self):
        return self._get_list_attr_value("$.mc_list[*].play_url.url_list[0]")

    @property
    def title(self):
        return replaceT(self._get_list_attr_value("$.mc_list[*].title"))

    @property
    def title_raw(self):
        return self._get_list_attr_value("$.mc_list[*].title")

    @property
    def strong_beat_url(self):
        return self._get_list_attr_value("$.mc_list[*].strong_beat_url.url_list[0]")

    @property
    def owner_nickname(self):
        return replaceT(self._get_list_attr_value("$.mc_list[*].owner_nickname"))

    @property
    def owner_nickname_raw(self):
        return self._get_list_attr_value("$.mc_list[*].owner_nickname")

    @property
    def owner_id(self):
        return self._get_list_attr_value("$.mc_list[*].owner_id")

    @property
    def sec_uid(self):
        return self._get_list_attr_value("$.mc_list[*].sec_uid")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields = [
            "has_more",
            "max_cursor",
            "status_code",
            "msg",
        ]

        extra_fields = [
            "has_more",
            "max_cursor",
            "status_code",
            "msg",
        ]

        list_dicts = filter_to_list(
            self,
            "$.mc_list",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class UserMixFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)

    @property
    def max_cursor(self):
        return self._get_attr_value("$.cursor")


class UserLikeFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)


class UserFollowingFilter(JSONModel):

    @property
    def status_code(self):  # 1 正常，2096 用户隐私设置不允许查看
        return self._get_attr_value("$.status_code")

    @property
    def status_msg(self):
        return self._get_attr_value("$.status_msg")

    @property
    def has_more(self):
        return self._get_attr_value("$.has_more")

    @property
    def total(self):
        return self._get_attr_value("$.total")

    @property
    def mix_count(self):
        return self._get_attr_value("$.mix_count")

    @property
    def offset(self):
        return self._get_attr_value("$.offset")

    @property
    def myself_user_id(self):
        return self._get_attr_value("$.myself_user_id")

    @property
    def max_time(self):
        return self._get_attr_value("$.max_time")

    @property
    def min_time(self):
        return self._get_attr_value("$.min_time")

    # following_list
    @property
    def avatar_larger(self):
        return self._get_list_attr_value("$.followings[*].avatar_larger.url_list[0]")

    @property
    def can_comment(self):
        return self._get_list_attr_value("$.followings[*].aweme_control.can_comment")

    @property
    def can_forward(self):
        return self._get_list_attr_value("$.followings[*].aweme_control.can_forward")

    @property
    def can_share(self):
        return self._get_list_attr_value("$.followings[*].aweme_control.can_share")

    @property
    def can_show_comment(self):
        return self._get_list_attr_value(
            "$.followings[*].aweme_control.can_show_comment"
        )

    @property
    def aweme_count(self):
        return self._get_list_attr_value("$.followings[*].aweme_count")

    @property
    def back_cover(self):
        return self._get_list_attr_value("$.followings[*].cover_url[0].url_list[0]")

    @property
    def register_time(self):
        return self._get_list_attr_value("$.followings[*].create_time")

    @property
    def secondary_priority(self):
        # secondary_priority 6 代表未看过的作品数量 1 代表正在直播 7 代表简介内容
        return self._get_list_attr_value(
            "$.followings[*].following_list_secondary_information_struct.secondary_information_priority"
        )

    @property
    def secondary_text(self):
        return replaceT(
            self._get_list_attr_value(
                "$.followings[*].following_list_secondary_information_struct.secondary_information_text"
            )
        )

    @property
    def secondary_text_raw(self):
        return self._get_list_attr_value(
            "$.followings[*].following_list_secondary_information_struct.secondary_information_text"
        )

    @property
    def is_block(self):
        return self._get_list_attr_value("$.followings[*].is_block")

    @property
    def is_blocked(self):
        return self._get_list_attr_value("$.followings[*].is_blocked")

    @property
    def is_gov_media_vip(self):
        return self._get_list_attr_value("$.followings[*].is_gov_media_vip")

    @property
    def is_mix_user(self):
        return self._get_list_attr_value("$.followings[*].is_mix_user")

    @property
    def is_phone_binded(self):
        return self._get_list_attr_value("$.followings[*].is_phone_binded")

    @property
    def is_star(self):
        return self._get_list_attr_value("$.followings[*].is_star")

    @property
    def is_top(self):
        # 超粉?
        return self._get_list_attr_value("$.followings[*].is_top")

    @property
    def is_verified(self):
        # 实名?
        return self._get_list_attr_value("$.followings[*].is_verified")

    @property
    def language(self):
        return self._get_list_attr_value("$.followings[*].language")

    @property
    def nickname(self):
        return replaceT(self._get_list_attr_value("$.followings[*].nickname"))

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.followings[*].nickname")

    @property
    def relation_label(self):
        return self._get_list_attr_value("$.followings[*].relation_label")

    @property
    def room_id(self):
        return self._get_list_attr_value("$.followings[*].room_id")

    @property
    def sec_uid(self):
        return self._get_list_attr_value("$.followings[*].sec_uid")

    @property
    def secret(self):
        # 私密?
        return self._get_list_attr_value("$.followings[*].secret")

    @property
    def short_id(self):
        return self._get_list_attr_value("$.followings[*].short_id")

    @property
    def signature(self):
        return replaceT(self._get_list_attr_value("$.followings[*].signature"))

    @property
    def signature_raw(self):
        return self._get_list_attr_value("$.followings[*].signature")

    @property
    def uid(self):
        return self._get_list_attr_value("$.followings[*].uid")

    @property
    def unique_id(self):
        return self._get_list_attr_value("$.followings[*].unique_id")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields = [
            "status_code",
            "status_msg",
            "has_more",
            "total",
            "mix_count",
            "offset",
            "myself_user_id",
            "max_time",
            "min_time",
        ]

        extra_fields = [
            "has_more",
            "total",
            "mix_count",
            "offset",
            "myself_user_id",
            "max_time",
            "min_time",
        ]

        list_dicts = filter_to_list(
            self,
            "$.followings",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class UserFollowerFilter(UserFollowingFilter):
    def __init__(self, data):
        super().__init__(data)

    @property
    def total(self):
        return self._get_attr_value("$.total")

    # followers
    @property
    def avatar_larger(self):
        return self._get_list_attr_value("$.followers[*].avatar_larger.url_list[0]")

    @property
    def can_comment(self):
        return self._get_list_attr_value("$.followers[*].aweme_control.can_comment")

    @property
    def can_forward(self):
        return self._get_list_attr_value("$.followers[*].aweme_control.can_forward")

    @property
    def can_share(self):
        return self._get_list_attr_value(
            "$.followersfollowers[*].aweme_control.can_share"
        )

    @property
    def can_show_comment(self):
        return self._get_list_attr_value(
            "$.followers[*].aweme_control.can_show_comment"
        )

    @property
    def aweme_count(self):
        return self._get_list_attr_value("$.followers[*].aweme_count")

    @property
    def back_cover(self):
        return self._get_list_attr_value("$.followers[*].cover_url[0].url_list[0]")

    @property
    def register_time(self):
        return self._get_list_attr_value("$.followers[*].create_time")

    @property
    def is_block(self):
        return self._get_list_attr_value("$.followers[*].is_block")

    @property
    def is_blocked(self):
        return self._get_list_attr_value("$.followers[*].is_blocked")

    @property
    def is_gov_media_vip(self):
        return self._get_list_attr_value("$.followers[*].is_gov_media_vip")

    @property
    def is_mix_user(self):
        return self._get_list_attr_value("$.followers[*].is_mix_user")

    @property
    def is_phone_binded(self):
        return self._get_list_attr_value("$.followers[*].is_phone_binded")

    @property
    def is_star(self):
        return self._get_list_attr_value("$.followers[*].is_star")

    @property
    def is_top(self):
        # 超粉?
        return self._get_list_attr_value("$.followers[*].is_top")

    @property
    def is_verified(self):
        # 实名?
        return self._get_list_attr_value("$.followers[*].is_verified")

    @property
    def language(self):
        return self._get_list_attr_value("$.followers[*].language")

    @property
    def nickname(self):
        return replaceT(self._get_list_attr_value("$.followers[*].nickname"))

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.followers[*].nickname")

    @property
    def relation_label(self):
        return self._get_list_attr_value("$.followers[*].relation_label")

    @property
    def room_id(self):
        return self._get_list_attr_value("$.followers[*].room_id")

    @property
    def sec_uid(self):
        return self._get_list_attr_value("$.followers[*].sec_uid")

    @property
    def secret(self):
        # 私密?
        return self._get_list_attr_value("$.followers[*].secret")

    @property
    def short_id(self):
        return self._get_list_attr_value("$.followers[*].short_id")

    @property
    def signature(self):
        return replaceT(self._get_list_attr_value("$.followers[*].signature"))

    @property
    def signature_raw(self):
        return self._get_list_attr_value("$.followers[*].signature")

    @property
    def uid(self):
        return self._get_list_attr_value("$.followers[*].uid")

    @property
    def unique_id(self):
        return self._get_list_attr_value("$.followers[*].unique_id")

    def _to_list(self) -> list:
        exclude_fields = [
            "status_code",
            "status_msg",
            "has_more",
            "total",
            "mix_count",
            "offset",
            "myself_user_id",
            "max_time",
            "min_time",
        ]

        extra_fields = [
            "has_more",
            "total",
            "mix_count",
            "offset",
            "myself_user_id",
            "max_time",
            "min_time",
        ]

        list_dicts = filter_to_list(
            self,
            "$.followers",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class PostDetailFilter(JSONModel):

    @property
    def api_status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def aweme_type(self):
        return self._get_attr_value("$.aweme_detail.aweme_type")

    @property
    def aweme_id(self):
        return self._get_attr_value("$.aweme_detail.aweme_id")

    # author
    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.aweme_detail.author.nickname"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.aweme_detail.author.nickname")

    @property
    def sec_user_id(self):
        return self._get_attr_value("$.aweme_detail.author.sec_uid")

    @property
    def short_id(self):
        return self._get_attr_value("$.aweme_detail.author.short_id")

    @property
    def uid(self):
        return self._get_attr_value("$.aweme_detail.author.uid")

    @property
    def unique_id(self):
        return self._get_attr_value("$.aweme_detail.author.unique_id")

    # aweme control
    @property
    def can_comment(self):
        return self._get_attr_value("$.aweme_detail.aweme_control.can_comment")

    @property
    def can_forward(self):
        return self._get_attr_value("$.aweme_detail.aweme_control.can_forward")

    @property
    def can_share(self):
        return self._get_attr_value("$.aweme_detail.aweme_control.can_share")

    @property
    def can_show_comment(self):
        return self._get_attr_value("$.aweme_detail.aweme_control.can_show_comment")

    # aweme detail
    @property
    def comment_gid(self):
        return self._get_attr_value("$.aweme_detail.comment_gid")

    @property
    def create_time(self):
        return timestamp_2_str(str(self._get_attr_value("$.aweme_detail.create_time")))

    @property
    def desc(self):
        return replaceT(self._get_attr_value("$.aweme_detail.desc"))

    @property
    def desc_raw(self):
        return self._get_attr_value("$.aweme_detail.desc")

    @property
    def duration(self):
        return self._get_attr_value("$.aweme_detail.duration")

    @property
    def is_ads(self):
        return self._get_attr_value("$.aweme_detail.is_ads")

    @property
    def is_story(self):
        return self._get_attr_value("$.aweme_detail.is_story")

    @property
    def is_top(self):
        return self._get_attr_value("$.aweme_detail.is_top")

    # aweme status
    @property
    def part_see(self):
        return self._get_attr_value("$.aweme_detail.status.part_see")

    @property
    def private_status(self):
        return self._get_attr_value("$.aweme_detail.status.private_status")

    @property
    def is_delete(self):
        return self._get_attr_value("$.aweme_detail.status.is_delete")

    @property
    def is_prohibited(self):
        return self._get_attr_value("$.aweme_detail.status.is_prohibited")

    # aweme video type
    # @property
    # def long_video(self):
    #     return self._get_attr_value("$.aweme_detail.long_video")

    @property
    def media_type(self):
        return self._get_attr_value("$.aweme_detail.media_type")

    # mix
    @property
    def mix_desc(self):
        return replaceT(self._get_attr_value("$.aweme_detail.mix_info.mix_desc"))

    @property
    def mix_desc_raw(self):
        return self._get_attr_value("$.aweme_detail.mix_info.mix_desc")

    @property
    def mix_create_time(self):
        return timestamp_2_str(
            str(self._get_attr_value("$.aweme_detail.mix_info.mix_create_time"))
        )

    @property
    def mix_id(self):
        return self._get_attr_value("$.aweme_detail.mix_info.mix_id")

    @property
    def mix_name(self):
        return self._get_attr_value("$.aweme_detail.mix_info.mix_name")

    @property
    def mix_pic_type(self):
        return self._get_attr_value("$.aweme_detail.mix_info.mix_pic_type")

    @property
    def mix_type(self):
        return self._get_attr_value("$.aweme_detail.mix_info.mix_type")

    @property
    def mix_share_url(self):
        return self._get_attr_value("$.aweme_detail.mix_info.mix_share_url")

    @property
    def mix_update_time(self):
        return timestamp_2_str(
            str(self._get_attr_value("$.aweme_detail.mix_info.mix_update_time"))
        )

    # music
    @property
    def is_commerce_music(self):
        return self._get_attr_value("$.aweme_detail.music.is_commerce_music")

    @property
    def is_original(self):
        return self._get_attr_value("$.aweme_detail.music.is_original")

    @property
    def is_original_sound(self):
        return self._get_attr_value("$.aweme_detail.music.is_original_sound")

    @property
    def is_pgc(self):
        return self._get_attr_value("$.aweme_detail.music.is_pgc")

    @property
    def music_author(self):
        return replaceT(self._get_attr_value("$.aweme_detail.music.author"))

    @property
    def music_author_raw(self):
        return self._get_attr_value("$.aweme_detail.music.author")

    @property
    def music_author_deleted(self):
        return self._get_attr_value("$.aweme_detail.music.author_deleted")

    @property
    def music_duration(self):
        return self._get_attr_value("$.aweme_detail.music.duration")

    @property
    def music_id(self):
        return self._get_attr_value("$.aweme_detail.music.id")

    @property
    def music_mid(self):
        return self._get_attr_value("$.aweme_detail.music.mid")

    @property
    def pgc_author(self):
        return replaceT(
            self._get_attr_value("$.aweme_detail.music.matched_pgc_sound.pgc_author")
        )

    @property
    def pgc_author_raw(self):
        return self._get_attr_value("$.aweme_detail.music.matched_pgc_sound.pgc_author")

    @property
    def pgc_author_title(self):
        return replaceT(
            self._get_attr_value(
                "$.aweme_detail.music.matched_pgc_sound.pgc_author_title"
            )
        )

    @property
    def pgc_author_title_raw(self):
        return self._get_attr_value(
            "$.aweme_detail.music.matched_pgc_sound.pgc_author_title"
        )

    @property
    def pgc_music_type(self):
        return self._get_attr_value(
            "$.aweme_detail.music.matched_pgc_sound.pgc_music_type"
        )

    @property
    def music_status(self):
        return self._get_attr_value("$.aweme_detail.music.status")

    @property
    def music_owner_handle(self):
        return replaceT(self._get_attr_value("$.aweme_detail.music.owner_handle"))

    @property
    def music_owner_handle_raw(self):
        return self._get_attr_value("$.aweme_detail.music.owner_handle")

    @property
    def music_owner_id(self):
        return self._get_attr_value("$.aweme_detail.music.owner_id")

    @property
    def music_owner_nickname(self):
        return replaceT(self._get_attr_value("$.aweme_detail.music.owner_nickname"))

    @property
    def music_owner_nickname_raw(self):
        return self._get_attr_value("$.aweme_detail.music.owner_nickname")

    @property
    def music_play_url(self):
        return self._get_attr_value("$.aweme_detail.music.play_url.url_list[0]")

    # position
    @property
    def position(self):
        return self._get_attr_value("$.aweme_detail.position")

    @property
    def region(self):
        return self._get_attr_value("$.aweme_detail.region")

    # seo_ocr_content
    @property
    def seo_ocr_content(self):
        return self._get_attr_value("$.aweme_detail.seo_info.seo_ocr_content")

    # video control
    @property
    def allow_douplus(self):
        return self._get_attr_value("$.aweme_detail.video_control.allow_douplus")

    @property
    def download_setting(self):
        return self._get_attr_value("$.aweme_detail.video_control.download_setting")

    @property
    def allow_share(self):
        return self._get_attr_value("$.aweme_detail.video_control.allow_share")

    # statistics
    @property
    def admire_count(self):
        return self._get_attr_value("$.aweme_detail.statistics.admire_count")

    @property
    def collect_count(self):
        return self._get_attr_value("$.aweme_detail.statistics.collect_count")

    @property
    def comment_count(self):
        return self._get_attr_value("$.aweme_detail.statistics.comment_count")

    @property
    def digg_count(self):
        return self._get_attr_value("$.aweme_detail.statistics.digg_count")

    # @property
    # def play_count(self):
    #     # 不从该接口获取
    #     return self._get_attr_value("$.aweme_detail.statistics.play_count")

    @property
    def share_count(self):
        return self._get_attr_value("$.aweme_detail.statistics.share_count")

    # text_extra
    @property
    def hashtag_ids(self):
        return self._get_list_attr_value(
            "$.aweme_detail.text_extra[*].hashtag_id", True
        )

    @property
    def hashtag_names(self):
        return self._get_list_attr_value(
            "$.aweme_detail.text_extra[*].hashtag_name", True
        )

    # video
    @property
    def animated_cover(self):
        return self._get_attr_value("$.aweme_detail.video.animated_cover.url_list[0]")

    @property
    def cover(self):
        return self._get_attr_value("$.aweme_detail.video.origin_cover.url_list[0]")

    @property
    def video_bit_rate(self):
        bit_rate_data = self._get_list_attr_value("$.aweme_detail.video.bit_rate")

        def extract_bit_rate(aweme):
            if not aweme:
                return []

            if isinstance(aweme, dict):
                return [aweme.get("bit_rate", 0)]

            if isinstance(aweme, list):
                return [item.get("bit_rate", 0) for item in aweme]

            return []

        return [extract_bit_rate(aweme) for aweme in bit_rate_data]

    @property
    def video_play_addr(self):
        return self._get_attr_value(
            "$.aweme_detail.video.bit_rate[0].play_addr.url_list"
        )

    # images
    @property
    def images(self):
        return self._get_list_attr_value("$.aweme_detail.images[*].url_list[0]")

    @property
    def images_video(self):
        return self._get_list_attr_value(
            "$.aweme_detail.images[*].video.play_addr.url_list[0]"
        )

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserLiveFilter(JSONModel):
    # live
    @property
    def api_status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def room_id(self):
        return self._get_attr_value("$.data.data[0].id_str")

    @property
    def live_status(self):
        return self._get_attr_value("$.data.data[0].status")

    @property
    def live_title(self):
        return replaceT(self._get_attr_value("$.data.data[0].title"))

    @property
    def live_title_raw(self):
        return self._get_attr_value("$.data.data[0].title")

    @property
    def cover(self):
        return self._get_attr_value("$.data.data[0].cover.url_list[0]")

    @property
    def user_count(self):
        return self._get_attr_value("$.data.data[0].stats.user_count_str")

    @property
    def total_user_count(self):
        return self._get_attr_value("$.data.data[0].stats.total_user_str")

    @property
    def like_count(self):
        return self._get_attr_value("$.data.data[0].stats.like_count_str")

    @property
    def flv_pull_url(self):
        return self._get_attr_value("$.data.data[0].stream_url.flv_pull_url")

    @property
    def m3u8_pull_url(self):
        return self._get_attr_value("$.data.data[0].stream_url.hls_pull_url_map")

    # author
    @property
    def user_id(self):
        return self._get_attr_value("$.data.data[0].owner.id_str")

    @property
    def sec_user_id(self):
        return self._get_attr_value("$.data.data[0].owner.sec_uid")

    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.data.data[0].owner.nickname"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.data.data[0].owner.nickname")

    @property
    def avatar_thumb(self):
        return self._get_attr_value("$.data.data[0].owner.avatar_thumb.url_list[0]")

    @property
    def follow_status(self):
        return self._get_attr_value("$.data.data[0].owner.follow_info.follow_status")

    # partition
    @property
    def partition_id(self):
        return self._get_attr_value(
            "$.data.data[0].partition_road_map.partition.id_str"
        )

    @property
    def partition_title(self):
        return self._get_attr_value("$.data.data[0].partition_road_map.partition.title")

    @property
    def sub_partition_id(self):
        return self._get_attr_value(
            "$.data.data[0].partition_road_map.sub_partition.id_str"
        )

    @property
    def sub_partition_title(self):
        return self._get_attr_value(
            "$.data.data[0].partition_road_map.sub_partition.title"
        )

    # room_auth
    @property
    def ChatAuth(self):
        return self._get_attr_value("$.data.data[0].room_auth.Chat")

    @property
    def GiftAuth(self):
        return self._get_attr_value("$.data.data[0].room_auth.Gift")

    @property
    def DiggAuth(self):
        return self._get_attr_value("$.data.data[0].room_auth.Digg")

    @property
    def ShareAuth(self):
        return self._get_attr_value("$.data.data[0].room_auth.Share")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserLive2Filter(JSONModel):
    # live
    @property
    def api_status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def room_id(self):
        return self._get_attr_value("$.data.room.id")

    @property
    def web_rid(self):
        return self._get_attr_value("$.data.room.owner.web_rid")

    @property
    def live_status(self):
        return self._get_attr_value("$.data.room.status")

    @property
    def live_title(self):
        return replaceT(self._get_attr_value("$.data.room.title"))

    @property
    def live_title_raw(self):
        return self._get_attr_value("$.data.room.title")

    @property
    def user_count(self):
        return self._get_attr_value("$.data.room.user_count")

    @property
    def create_time(self):
        return timestamp_2_str(str(self._get_attr_value("$.data.room.create_time")))

    @property
    def finish_time(self):
        return timestamp_2_str(str(self._get_attr_value("$.data.room.finish_time")))

    @property
    def cover(self):
        return self._get_attr_value("$.data.room.cover.url_list[0]")

    @property
    def stream_id(self):
        return self._get_attr_value("$.data.room.stream_id")

    @property
    def resolution_name(self):
        return self._get_attr_value("$.data.room.stream_url.resolution_name")

    @property
    def flv_pull_url(self):
        return self._get_attr_value("$.data.room.stream_url.flv_pull_url")

    @property
    def hls_pull_url(self):
        return self._get_attr_value("$.data.room.stream_url.hls_pull_url_map")

    # user
    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.data.room.owner.nickname"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.data.room.owner.nickname")

    @property
    def gender(self):
        return replaceT(self._get_attr_value("$.data.room.owner.gender"))

    @property
    def gender_raw(self):
        return self._get_attr_value("$.data.room.owner.gender")

    @property
    def signature(self):
        return replaceT(self._get_attr_value("$.data.room.owner.signature"))

    @property
    def signature_raw(self):
        return self._get_attr_value("$.data.room.owner.signature")

    @property
    def avatar_large(self):
        return self._get_attr_value("$.data.room.owner.avatar_large.url_list[0]")

    @property
    def verified(self):
        return self._get_attr_value("$.data.room.owner.verified")

    @property
    def city(self):
        return self._get_attr_value("$.data.room.owner.city")

    @property
    def following_count(self):
        return self._get_attr_value("$.data.room.owner.follow_info.following_count")

    @property
    def follower_count(self):
        return self._get_attr_value("$.data.room.owner.follow_info.follower_count")

    @property
    def sec_uid(self):
        return self._get_attr_value("$.data.room.owner.sec_uid")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class PostRelatedFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)


class FriendFeedFilter(JSONModel):
    # 8 login_expired
    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def status_msg(self):
        return self._get_attr_value("$.status_msg")

    @property
    def toast(self):
        return self._get_attr_value("$.toast")

    @property
    def has_more(self):
        return bool(self._get_attr_value("$.has_more"))

    @property
    def has_aweme(self):
        return bool(self._get_attr_value("$.data"))

    @property
    def friend_update_count(self):
        return self._get_attr_value("$.friend_update_count")

    @property
    def cursor(self):
        return self._get_attr_value("$.cursor")

    @property
    def level(self):
        return self._get_attr_value("$.level")

    @property
    def friend_feed_type(self):
        return self._get_list_attr_value("$.data[*].feed_type")

    @property
    def friend_feed_source(self):
        return self._get_list_attr_value("$.data[*].source")

    # user
    @property
    def avatar_larger(self):
        return self._get_list_attr_value(
            "$.data[*].aweme.author.avatar_larger.url_list[0]"
        )

    @property
    def nickname(self):
        return replaceT(self._get_list_attr_value("$.data[*].aweme.author.nickname"))

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.data[*].aweme.author.nickname")

    @property
    def sec_uid(self):
        return self._get_list_attr_value("$.data[*].aweme.author.sec_uid")

    @property
    def uid(self):
        return self._get_list_attr_value("$.data[*].aweme.author.uid")

    # aweme
    @property
    def aweme_id(self):
        return self._get_list_attr_value("$.data[*].aweme.aweme_id")

    @property
    def aweme_type(self):
        return self._get_list_attr_value("$.data[*].aweme.aweme_type")

    @property
    def desc(self):
        return replaceT(self._get_list_attr_value("$.data[*].aweme.desc"))

    @property
    def desc_raw(self):
        return self._get_list_attr_value("$.data[*].aweme.desc")

    @property
    def recommend_reason(self):
        return self._get_list_attr_value(
            "$.data[*].aweme.fall_card_struct.recommend_reason"
        )

    @property
    def create_time(self):
        create_times = self._get_list_attr_value("$.data[*].aweme.create_time")
        return (
            [timestamp_2_str(str(ct)) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(str(create_times))
        )

    @property
    def is_24_story(self):  # 是否是24小时动态
        return self._get_list_attr_value("$.data[*].aweme.is_24_story")

    @property
    def media_type(self):
        return self._get_list_attr_value("$.data[*].aweme.media_type")

    @property
    def collect_count(self):
        return self._get_list_attr_value("$.data[*].aweme.statistics.collect_count")

    @property
    def comment_count(self):
        return self._get_list_attr_value("$.data[*].aweme.statistics.comment_count")

    @property
    def digg_count(self):
        return self._get_list_attr_value("$.data[*].aweme.statistics.digg_count")

    @property
    def exposure_count(self):
        return self._get_list_attr_value("$.data[*].aweme.statistics.exposure_count")

    @property
    def live_watch_count(self):
        return self._get_list_attr_value("$.data[*].aweme.statistics.live_watch_count")

    @property
    def play_count(self):
        return self._get_list_attr_value("$.data[*].aweme.statistics.play_count")

    @property
    def share_count(self):
        return self._get_list_attr_value("$.data[*].aweme.statistics.share_count")

    @property
    def allow_share(self):
        return self._get_list_attr_value("$.data[*].aweme.status.allow_share")

    @property
    def private_status(self):
        return self._get_list_attr_value("$.data[*].aweme.status.private_status")

    @property
    def is_prohibited(self):
        return self._get_list_attr_value("$.data[*].aweme.status.is_prohibited")

    @property
    def part_see(self):
        return self._get_list_attr_value("$.data[*].aweme.status.part_see")

    # video
    @property
    def animated_cover(self):
        # 获取所有视频
        videos = self._get_list_attr_value("$.data[*].aweme.video")

        # 逐个视频判断是否存在animated_cover
        animated_covers = [
            (
                video.get("animated_cover", {}).get("url_list", [None])[0]
                if video.get("animated_cover")
                else None
            )
            for video in videos
        ]

        return animated_covers

    @property
    def cover(self):
        return self._get_list_attr_value("$.data[*].aweme.video.cover.url_list[0]")

    @property
    def images(self):
        images_list = self._get_list_attr_value("$.data[*].aweme.images")
        return [
            (
                [
                    img["url_list"][0]
                    for img in images
                    if isinstance(img, dict) and "url_list" in img and img["url_list"]
                ]
                if images
                else None
            )
            for images in images_list
        ]

    @property
    def images_video(self):
        images_list = self._get_list_attr_value("$.data[*].aweme.images")
        return [
            (
                [
                    img["video"]["play_addr"]["url_list"][0]
                    for img in images
                    if isinstance(img, dict) and "video" in img
                ]
                if images
                else None
            )
            for images in images_list
        ]

    @property
    def video_play_addr(self):
        return self._get_list_attr_value(
            "$.data[*].aweme.video.bit_rate[0].play_addr.url_list"
        )

    # music
    @property
    def music_id(self):
        return self._get_list_attr_value("$.data[*].aweme.music.id")

    @property
    def music_mid(self):
        return self._get_list_attr_value("$.data[*].aweme.music.mid")

    @property
    def music_duration(self):
        return self._get_list_attr_value("$.data[*].aweme.music.duration")

    @property
    def music_play_url(self):
        return self._get_list_attr_value("$.data[*].aweme.music.play_url.url_list[0]")

    @property
    def music_owner_nickname(self):
        return replaceT(
            self._get_list_attr_value("$.data[*].aweme.music.owner_nickname")
        )

    @property
    def music_owner_nickname_raw(self):
        return self._get_list_attr_value("$.data[*].aweme.music.owner_nickname")

    @property
    def music_sec_uid(self):
        return self._get_list_attr_value("$.data[*].aweme.music.sec_uid")

    @property
    def music_title(self):
        return replaceT(self._get_list_attr_value("$.data[*].aweme.music.title"))

    @property
    def music_title_raw(self):
        return self._get_list_attr_value("$.data[*].aweme.music.title")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields = [
            "status_code",
            "status_msg",
            "has_more",
            "has_aweme",
            "friend_update_count",
            "cursor",
            "level",
        ]
        extra_fields = [
            "has_more",
            "has_aweme",
            "friend_update_count",
            "cursor",
            "level",
        ]

        list_dicts = filter_to_list(
            self,
            "$.data",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class GetQrcodeFilter(JSONModel):
    @property
    def app_name(self):
        return self._get_attr_value("$.data.app_name")

    @property
    def access_key(self):
        return self._get_attr_value("$.data.frontier_params.access_key")

    @property
    def frontier_device(self):
        return self._get_attr_value("$.data.frontier_params.frontier_device")

    @property
    def method(self):
        return self._get_attr_value("$.data.frontier_params.method")

    @property
    def product_id(self):
        return self._get_attr_value("$.data.frontier_params.product_id")

    @property
    def service_id(self):
        return self._get_attr_value("$.data.frontier_params.service_id")

    @property
    def is_frontier(self):
        return self._get_attr_value("$.data.is_frontier")

    @property
    def qrcode(self):
        return self._get_attr_value("$.data.qrcode")  # base64

    @property
    def qrcode_index_url(self):
        return self._get_attr_value("$.data.qrcode_index_url")

    @property
    def token(self):
        return self._get_attr_value("$.data.token")

    @property
    def web_name(self):
        return self._get_attr_value("$.data.web_name")

    @property
    def description(self):
        return self._get_attr_value("$.description")

    @property
    def error_code(self):
        return self._get_attr_value("$.error_code")

    @property
    def message(self):
        return self._get_attr_value("$.message")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class CheckQrcodeFilter(JSONModel):
    @property
    def extra(self):
        return self._get_attr_value("$.data.extra")

    @property
    def status(self):
        return self._get_attr_value("$.data.status")

    @property
    def redirect_url(self):
        return self._get_attr_value("$.data.redirect_url")

    @property
    def description(self):
        return self._get_attr_value("$.description")

    @property
    def error_code(self):
        return self._get_attr_value("$.error_code")

    @property
    def message(self):
        return self._get_attr_value("$.message")

    @property
    def verify_ticket(self):
        return self._get_attr_value("$.verify_ticket")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class LiveImFetchFilter(JSONModel):
    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def is_show_msg(self):
        return self._get_attr_value("$.data[0].common.is_show_msg")

    @property
    def msg_id(self):
        return self._get_attr_value("$.data[0].common.msg_id")

    @property
    def room_id(self):
        return self._get_attr_value("$.data[0].common.room_id")

    @property
    def internal_ext(self):
        return self._get_attr_value("$.internal_ext")

    @property
    def cursor(self):
        return self._get_attr_value("$.extra.cursor")

    @property
    def now(self):
        return timestamp_2_str(str(self._get_attr_value("$.extra.now")))

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class QueryUserFilter(JSONModel):
    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def status_msg(self):
        return self._get_attr_value("$.status_msg")

    @property
    def browser_name(self):
        return self._get_attr_value("$.browser_name")

    @property
    def create_time(self):
        return timestamp_2_str(str(self._get_attr_value("$.create_time")))

    @property
    def firebase_instance_id(self):
        return self._get_attr_value("$.firebase_instance_id")

    @property
    def user_unique_id(self):
        return self._get_attr_value("$.id")

    @property
    def last_time(self):
        return timestamp_2_str(str(self._get_attr_value("$.last_time")))

    @property
    def user_agent(self):
        return self._get_attr_value("$.user_agent")

    @property
    def user_uid(self):
        return self._get_attr_value("$.user_uid")

    @property
    def user_uid_type(self):
        return self._get_attr_value("$.user_uid_type")

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class FollowingUserLiveFilter(JSONModel):
    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def status_msg(self):
        return self._get_attr_value("$.data.message")

    @property
    def cover_type(self):
        return self._get_list_attr_value("$.data.data.[*].cover_type")

    @property
    def is_recommend(self):
        return self._get_list_attr_value("$.data.data.[*].is_recommend")

    @property
    def tag_name(self):
        return self._get_list_attr_value("$.data.data.[*].tag_name")

    @property
    def title_type(self):
        return self._get_list_attr_value("$.data.data.[*].title_type")

    @property
    def uniq_id(self):
        return self._get_list_attr_value("$.data.data.[*].uniq_id")

    @property
    def web_rid(self):
        return self._get_list_attr_value("$.data.data.[*].web_rid")

    @property
    def cover(self):
        return self._get_list_attr_value("$.data.data.[*].room.cover.url_list[0]")

    @property
    def has_commerce_goods(self):
        return self._get_list_attr_value("$.data.data.[*].room.has_commerce_goods")

    @property
    def room_id(self):
        return self._get_list_attr_value("$.data.data.[*].room.id_str")

    @property
    def live_title(self):
        return replaceT(self._get_list_attr_value("$.data.data.[*].room.title"))

    @property
    def live_title_raw(self):
        return self._get_list_attr_value("$.data.data.[*].room.title")

    @property
    def live_room_mode(self):
        return self._get_list_attr_value("$.data.data.[*].room.live_room_mode")

    @property
    def mosaic_status(self):
        return self._get_list_attr_value("$.data.data.[*].room.mosaic_status")

    @property
    def user_count(self):
        return self._get_list_attr_value("$.data.data.[*].room.stats.user_count_str")

    @property
    def like_count(self):
        return self._get_list_attr_value("$.data.data.[*].room.stats.like_count")

    @property
    def total_count(self):
        return self._get_list_attr_value("$.data.data.[*].room.stats.total_user_str")

    # user
    @property
    def avatar_thumb(self):
        return self._get_list_attr_value(
            "$.data.data.[*].room.owner.avatar_thumb.url_list[0]"
        )

    @property
    def user_id(self):
        return self._get_list_attr_value("$.data.data.[*].room.owner.id_str")

    @property
    def user_sec_uid(self):
        return self._get_list_attr_value("$.data.data.[*].room.owner.sec_uid")

    @property
    def nickname(self):
        return replaceT(
            self._get_list_attr_value("$.data.data.[*].room.owner.nickname")
        )

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.data.data.[*].room.owner.nickname")

    # stream_url
    @property
    def flv_pull_url(self):
        return self._get_list_attr_value("$.data.data.[*].room.stream_url.flv_pull_url")

    @property
    def hls_pull_url(self):
        return self._get_list_attr_value(
            "$.data.data.[*].room.stream_url.hls_pull_url_map"
        )

    @property
    def stream_orientation(self):
        return self._get_list_attr_value(
            "$.data.data.[*].room.stream_url.stream_orientation"
        )

    def _to_raw(self) -> Dict:
        return self._data

    def _to_dict(self) -> Dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields = [
            "status_code",
            "status_msg",
        ]
        extra_fields = []

        list_dicts = filter_to_list(
            self,
            "$.data.data",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class PostStatsFilter(JSONModel):

    # 0 正常 5 参数不合法 2863 您的操作过于频繁，请稍后再试
    @property
    def status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def status_msg(self):
        return self._get_attr_value("$.status_msg")
