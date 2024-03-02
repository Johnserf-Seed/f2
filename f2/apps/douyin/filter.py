from f2.utils.json_filter import JSONModel
from f2.utils.utils import _get_first_item_from_list, timestamp_2_str, replaceT

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

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserPostFilter(JSONModel):
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
            [timestamp_2_str(ct) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(create_times)
        )

    @property
    def desc(self):
        return replaceT(self._get_list_attr_value("$.aweme_list[*].desc"))

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
        return self._get_list_attr_value("$.aweme_list[*].video.play_addr.url_list[0]")

    @property
    def video_bit_rate(self):
        bit_rate_data = self._get_list_attr_value("$.aweme_list[*].video.bit_rate")

        return [
            (
                [aweme["bit_rate"]]
                if isinstance(aweme, dict)
                else (
                    [aweme[0]["bit_rate"]]
                    if len(aweme) == 1
                    else [item["bit_rate"] for item in aweme]
                )
            )
            for aweme in bit_rate_data
        ]

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
    def music_play_url(self):
        url_list = self._get_list_attr_value("$.aweme_list[*].music.play_url.url_list")
        return _get_first_item_from_list(url_list)

    @property
    def has_more(self) -> bool:
        return bool(self._get_attr_value("$.has_more"))

    @property
    def max_cursor(self):
        return self._get_attr_value("$.max_cursor")

    @property
    def min_cursor(self):
        return self._get_attr_value("$.min_cursor")

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self):
        exclude_list = [
            "has_more",
            "max_cursor",
            "min_cursor",
            "has_aweme",
            "locate_item_cursor",
        ]

        keys = [
            prop_name
            for prop_name in dir(self)
            if not prop_name.startswith("__")
            and not prop_name.startswith("_")
            and prop_name not in exclude_list
        ]

        aweme_entries = self._get_attr_value("$.aweme_list") or []

        list_dicts = []
        for entry in aweme_entries:
            d = {
                "has_more": self.has_more,
                "max_cursor": self.max_cursor,
                "min_cursor": self.min_cursor,
            }
            for key in keys:
                attr_values = getattr(self, key)
                index = aweme_entries.index(entry)
                d[key] = attr_values[index] if index < len(attr_values) else None
            list_dicts.append(d)
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
    def total_number(self):
        return self._get_attr_value("$.total_number")

    @property
    def has_more(self):
        return bool(self._get_attr_value("$.has_more"))

    @property
    def app_id(self):
        return self._get_attr_value("$.collects_list[*].app_id")

    @property
    def collects_cover(self):
        return self._get_attr_value("$.collects_list[*].collects_cover.url_list[0]")

    @property
    def collects_id(self):
        return self._get_attr_value("$.collects_list[*].collects_id")

    @property
    def collects_name(self):
        return self._get_attr_value("$.collects_list[*].collects_name")

    @property
    def create_time(self):
        return timestamp_2_str(self._get_attr_value("$.collects_list[*].create_time"))

    @property
    def follow_status(self):
        return self._get_attr_value("$.collects_list[*].follow_status")

    @property
    def followed_count(self):
        return self._get_attr_value("$.collects_list[*].followed_count")

    @property
    def is_normal_status(self):
        return self._get_attr_value("$.collects_list[*].is_normal_status")

    @property
    def item_type(self):
        return self._get_attr_value("$.collects_list[*].item_type")

    @property
    def last_collect_time(self):
        return timestamp_2_str(
            self._get_attr_value("$.collects_list[*].last_collect_time")
        )

    @property
    def play_count(self):
        return self._get_attr_value("$.collects_list[*].play_count")

    @property
    def states(self):
        return self._get_attr_value("$.collects_list[*].states")

    @property
    def status(self):
        return self._get_attr_value("$.collects_list[*].status")

    @property
    def system_type(self):
        return self._get_attr_value("$.collects_list[*].system_type")

    @property
    def total_number(self):
        return self._get_attr_value("$.collects_list[*].total_number")

    @property
    def user_id(self):
        return self._get_attr_value("$.collects_list[*].user_id")

    # user_info
    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.collects_list[*].user_info.nickname"))

    @property
    def uid(self):
        return self._get_attr_value("$.collects_list[*].user_info.uid")

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserMixFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)

    @property
    def max_cursor(self):
        return self._get_attr_value("$.cursor")


class UserLikeFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)


class PostDetailFilter(JSONModel):
    # api_status_code = property(lambda self: self._get_attr_value("$.status_code"))
    # # author
    # nickname = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.author.nickname")))
    # sec_user_id = property(lambda self: self._get_attr_value("$.aweme_detail.author.sec_uid"))
    # short_id = property(lambda self: self._get_attr_value("$.aweme_detail.author.short_id"))
    # uid = property(lambda self: self._get_attr_value("$.aweme_detail.author.uid"))
    # unique_id = property(lambda self: self._get_attr_value("$.aweme_detail.author.unique_id"))

    # can_comment = property(lambda self: self._get_attr_value("$.aweme_detail.aweme_control.can_comment"))
    # can_forward = property(lambda self: self._get_attr_value("$.aweme_detail.aweme_control.can_forward"))
    # can_share = property(lambda self: self._get_attr_value("$.aweme_detail.aweme_control.can_share"))
    # can_show_comment = property(lambda self: self._get_attr_value("$.aweme_detail.aweme_control.can_show_comment"))
    # aweme_type = property(lambda self: self._get_attr_value("$.aweme_detail.aweme_control.aweme_type"))
    # aweme_id = property(lambda self: self._get_attr_value("$.aweme_detail.aweme_id"))
    # comment_gid = property(lambda self: self._get_attr_value("$.aweme_detail.comment_gid"))
    # create_time = property(lambda self: timestamp_2_str(self._get_attr_value("$.aweme_detail.create_time")))
    # desc = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.desc")))
    # duration = property(lambda self: self._get_attr_value("$.aweme_detail.duration"))
    # is_ads = property(lambda self: self._get_attr_value("$.aweme_detail.is_ads"))
    # is_story = property(lambda self: self._get_attr_value("$.aweme_detail.is_story"))
    # is_top = property(lambda self: self._get_attr_value("$.aweme_detail.is_top"))
    # video_bit_rate = property(lambda self: [
    #     [aweme['bit_rate']] if isinstance(aweme, dict)
    #     else [aweme[0]['bit_rate']] if len(aweme) == 1
    #     else [item['bit_rate'] for item in aweme]
    #     for aweme in self._get_list_attr_value("$.aweme_detail.video.bit_rate")
    # ])
    # video_play_addr = property(lambda self: self._get_attr_value("$.aweme_detail.video.play_addr.url_list[0]"))
    # images = property(lambda self: [
    #     [img['url_list'][0] for img in images if isinstance(img, dict) and 'url_list' in img and img['url_list']]
    #     if images else None
    #     for images in self._get_list_attr_value("$.aweme_detail.images")
    # ])

    # # aweme status
    # is_delete = property(lambda self: self._get_attr_value("$.aweme_detail.status.is_delete"))
    # is_prohibited = property(lambda self: self._get_attr_value("$.aweme_detail.status.is_prohibited"))

    # is_long_video = property(lambda self: self._get_attr_value("$.aweme_detail.long_video"))
    # media_type = property(lambda self: self._get_attr_value("$.aweme_detail.media_type"))
    # # mix
    # mix_desc = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.mix_info.mix_desc")))
    # mix_create_time = property(lambda self: timestamp_2_str(self._get_attr_value("$.aweme_detail.mix_info.mix_create_time")))
    # mix_id = property(lambda self: self._get_attr_value("$.aweme_detail.mix_info.mix_id"))
    # mix_name = property(lambda self: self._get_attr_value("$.aweme_detail.mix_info.mix_name"))
    # mix_pic_type = property(lambda self: self._get_attr_value("$.aweme_detail.mix_info.mix_pic_type"))
    # mix_type = property(lambda self: self._get_attr_value("$.aweme_detail.mix_info.mix_type"))
    # mix_share_url = property(lambda self: self._get_attr_value("$.aweme_detail.mix_info.mix_share_url"))
    # mix_update_time = property(lambda self: timestamp_2_str(self._get_attr_value("$.aweme_detail.mix_info.mix_update_time")))
    # # music
    # is_commerce_music = property(lambda self: self._get_attr_value("$.aweme_detail.music.is_commerce_music"))
    # is_original = property(lambda self: self._get_attr_value("$.aweme_detail.music.is_original"))
    # is_original_sound = property(lambda self: self._get_attr_value("$.aweme_detail.music.is_original_sound"))
    # is_pgc = property(lambda self: self._get_attr_value("$.aweme_detail.music.is_pgc"))
    # music_author = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.music.author")))
    # music_author_deleted = property(lambda self: self._get_attr_value("$.aweme_detail.music.author_deleted"))
    # music_duration = property(lambda self: self._get_attr_value("$.aweme_detail.music.duration"))
    # music_id = property(lambda self: self._get_attr_value("$.aweme_detail.music.id"))
    # music_id_str = property(lambda self: self._get_attr_value("$.aweme_detail.music.id_str"))
    # music_mid = property(lambda self: self._get_attr_value("$.aweme_detail.music.mid"))
    # pgc_author = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.music.matched_pgc_sound.pgc_author")))
    # pgc_author_title = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.music.matched_pgc_sound.pgc_author_title")))
    # pgc_music_type = property(lambda self: self._get_attr_value("$.aweme_detail.music.matched_pgc_sound.pgc_music_type"))
    # music_status = property(lambda self: self._get_attr_value("$.aweme_detail.music.status"))
    # music_owner_handle = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.music.owner_handle")))
    # music_owner_id = property(lambda self: self._get_attr_value("$.aweme_detail.music.owner_id"))
    # music_owner_nickname = property(lambda self: replaceT(self._get_attr_value("$.aweme_detail.music.owner_nickname")))
    # music_play_url = property(lambda self: self._get_attr_value("$.aweme_detail.music.play_url.url_list[0]"))

    # # position
    # position = property(lambda self: self._get_attr_value("$.aweme_detail.position"))
    # # region = property(lambda self: self._get_attr_value("$.aweme_detail.region"))

    # # seo_ocr_content
    # seo_ocr_content = property(lambda self: self._get_attr_value("$.aweme_detail.seo_info.seo_ocr_content"))

    # admire_count = property(lambda self: self._get_attr_value("$.aweme_detail.statistics.admire_count"))
    # collect_count = property(lambda self: self._get_attr_value("$.aweme_detail.statistics.collect_count"))
    # comment_count = property(lambda self: self._get_attr_value("$.aweme_detail.statistics.comment_count"))
    # digg_count = property(lambda self: self._get_attr_value("$.aweme_detail.statistics.digg_count"))
    # # play_count = property(lambda self: self._get_attr_value("$.aweme_detail.statistics.play_count"))
    # share_count = property(lambda self: self._get_attr_value("$.aweme_detail.statistics.share_count"))

    # hashtag_ids = property(lambda self: self._get_list_attr_value("$.aweme_detail.text_extra[*].hashtag_id"))
    # hashtag_names = property(lambda self: self._get_list_attr_value("$.aweme_detail.text_extra[*].hashtag_name"))

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
    def pgc_author_title(self):
        return replaceT(
            self._get_attr_value(
                "$.aweme_detail.music.matched_pgc_sound.pgc_author_title"
            )
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
    def music_owner_id(self):
        return self._get_attr_value("$.aweme_detail.music.owner_id")

    @property
    def music_owner_nickname(self):
        return replaceT(self._get_attr_value("$.aweme_detail.music.owner_nickname"))

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
        bit_rate_data = self._get_list_attr_value(
            "$.aweme_detail.video.bit_rate",
        )

        return [
            (
                [aweme["bit_rate"]]
                if isinstance(aweme, dict)
                else (
                    [aweme[0]["bit_rate"]]
                    if len(aweme) == 1
                    else [item["bit_rate"] for item in aweme]
                )
            )
            for aweme in bit_rate_data
        ]

    @property
    def video_play_addr(self):
        return self._get_attr_value("$.aweme_detail.video.play_addr.url_list[0]")

    # images
    @property
    def images(self):
        return self._get_list_attr_value("$.aweme_detail.images[*].url_list[0]")

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self):
        # 不需要的属性列表
        exclude_list = ["has_more", "max_cursor", "min_cursor"]
        # 生成属性名称列表，然后过滤掉不需要的属性
        keys = [
            prop_name
            for prop_name in dir(self)
            if not prop_name.startswith("__")
            and not prop_name.startswith("_")
            and prop_name not in exclude_list
        ]

        aweme_entries = self._get_attr_value("$.aweme_detail") or []

        list_dicts = []
        # 遍历每个条目并创建一个字典
        # (Iterate through each entry and create a dict)
        for entry in aweme_entries:
            d = {}
            for key in keys:
                attr_values = getattr(self, key)
                # 当前aweme_entry在属性列表中的索引
                index = aweme_entries.index(entry)
                # 如果属性值的长度足够则赋值，否则赋None
                # (Assign value if the length of the attribute value is sufficient, otherwise assign None)
                d[key] = attr_values[index] if index < len(attr_values) else None
            list_dicts.append(d)
        return list_dicts


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

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self):
        # 不需要的属性列表
        exclude_list = []
        # 生成属性名称列表，然后过滤掉不需要的属性
        keys = [
            prop_name
            for prop_name in dir(self)
            if not prop_name.startswith("__")
            and not prop_name.startswith("_")
            and prop_name not in exclude_list
        ]

        aweme_entries = self._get_attr_value("$.aweme_list") or []

        list_dicts = []
        # 遍历每个条目并创建一个字典
        # (Iterate through each entry and create a dict)
        for entry in aweme_entries:
            d = {}
            for key in keys:
                attr_values = getattr(self, key)
                # 当前aweme_entry在属性列表中的索引
                index = aweme_entries.index(entry)
                # 如果属性值的长度足够则赋值，否则赋None
                # (Assign value if the length of the attribute value is sufficient, otherwise assign None)
                d[key] = attr_values[index] if index < len(attr_values) else None
            list_dicts.append(d)
        return list_dicts


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
    def user_count(self):
        return self._get_attr_value("$.data.room.user_count")

    @property
    def create_time(self):
        return timestamp_2_str(self._get_attr_value("$.data.room.create_time"))

    @property
    def finish_time(self):
        return timestamp_2_str(self._get_attr_value("$.data.room.finish_time"))

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
    def gender(self):
        return replaceT(self._get_attr_value("$.data.room.owner.gender"))

    @property
    def signature(self):
        return replaceT(self._get_attr_value("$.data.room.owner.signature"))

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

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


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

    def _to_dict(self) -> dict:
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

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }
