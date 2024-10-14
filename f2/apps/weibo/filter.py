# path: f2/apps/weibo/filter.py

from f2.utils.json_filter import JSONModel
from f2.utils.utils import timestamp_2_str, replaceT

# Filter


class UserInfoFilter(JSONModel):

    @property
    def status(self):
        return self._get_attr_value("$.data.ok")

    @property
    def blockText(self):
        return self._get_attr_value("$.data.blockText")

    @property
    def avatar_hd(self):
        return self._get_attr_value("$.data.user.avatar_hd")

    @property
    def cover_image(self):
        return self._get_attr_value("$.data.user.cover_image_phone")

    @property
    def description(self):
        return replaceT(self._get_attr_value("$.data.user.description"))

    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.data.user.screen_name"))

    @property
    def follow_me(self):
        return self._get_attr_value("$.data.user.follow_me")

    @property
    def following(self):
        return self._get_attr_value("$.data.user.following")

    @property
    def followers_count(self):
        return self._get_attr_value("$.data.user.followers_count")

    @property
    def friends_count(self):
        return self._get_attr_value("$.data.user.friends_count")

    @property
    def weibo_count(self):
        return self._get_attr_value("$.data.user.statuses_count")

    @property
    def gender(self):
        return self._get_attr_value("$.data.user.gender")

    @property
    def uid(self):
        return self._get_attr_value("$.data.user.idstr")

    @property
    def weihao(self):
        return self._get_attr_value("$.data.user.weihao")

    @property
    def is_muteuser(self):
        return self._get_attr_value("$.data.user.is_muteuser")

    @property
    def is_star(self):
        return self._get_attr_value("$.data.user.is_star")

    @property
    def location(self):
        return self._get_attr_value("$.data.user.location")

    @property
    def profile_url(self):
        return "https://weibo.com" + self._get_attr_value("$.data.user.profile_url")

    @property
    def user_type(self):
        return self._get_attr_value("$.data.user.user_type")

    @property
    def verified(self):
        return self._get_attr_value("$.data.user.verified")

    @property
    def vvip(self):
        return self._get_attr_value("$.data.user.vvip")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserDetailFilter(JSONModel):

    @property
    def status(self):
        return self._get_attr_value("$.ok")

    @property
    def message(self):
        return self._get_attr_value("$.message")

    @property
    def birthday(self):
        return self._get_attr_value("$.data.birthday")

    @property
    def description(self):
        return replaceT(self._get_attr_value("$.data.description"))

    @property
    def description_raw(self):
        return self._get_attr_value("$.data.description")

    @property
    def location(self):
        return self._get_attr_value("$.data.ip_location")

    @property
    def gender(self):
        return self._get_attr_value("$.data.gender")

    @property
    def create_at(self):
        return self._get_attr_value("$.data.created_at").replace(":", "-")

    @property
    def video_play_count(self):
        return self._get_attr_value("$.data.label_desc[0].name")

    @property
    def real_name(self):
        return self._get_attr_value("$.data.real_name.name")

    @property
    def sunshine_credit(self):
        return self._get_attr_value("$.data.sunshine_credit.level")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class WeiboDetailFilter(JSONModel):

    @property
    def status(self):
        return self._get_attr_value("$.ok")

    @property
    def message(self):
        return self._get_attr_value("$.message")

    @property
    def error_code(self):
        return self._get_attr_value("$.error_code")

    @property
    def weibo_id(self):
        return self._get_attr_value("$.idstr")

    @property
    def weibo_blog_id(self):
        return self._get_attr_value("$.mblogid")

    @property
    def weibo_type(self):
        return self._get_attr_value("$.mblogtype")

    @property
    def rid(self):
        return self._get_attr_value("$.rid")

    @property
    def create_time(self):
        return timestamp_2_str(self._get_attr_value("$.created_at"))

    @property
    def desc(self):
        return replaceT(self._get_attr_value("$.text"))

    @property
    def descLength(self):
        return self._get_attr_value("$.textLength")

    @property
    def descRaw(self):
        return replaceT(self._get_attr_value("$.text_raw"))

    @property
    def descRaw_raw(self):
        return self._get_attr_value("$.text_raw")

    @property
    def digg_count(self):
        return self._get_attr_value("$.attitudes_count")

    @property
    def comments_count(self):
        return self._get_attr_value("$.comments_count")

    @property
    def share_count(self):
        return self._get_attr_value("$.reposts_count")

    # IMG
    @property
    def pic_ids(self):
        return self._get_attr_value("$.pic_ids")

    @property
    def pic_num(self):
        return self._get_attr_value("$.pic_num")

    @property
    def pic_infos(self):
        # 每个图片的信息都是pic_ids作为下标的
        return self._get_attr_value("$.pic_infos")

    # VIDEO
    @property
    def bitrate_list(self):
        return self._get_list_attr_value(
            "$.page_info.media_info.playback_list[*].play_info.bitrate"
        )

    @property
    def playback_list(self):
        return self._get_list_attr_value(
            "$.page_info.media_info.playback_list[*].play_info.url"
        )

    @property
    def quality_list(self):
        return self._get_list_attr_value(
            "$.page_info.media_info.playback_list[*].play_info.quality_class"
        )

    @property
    def region(self):
        return self._get_attr_value("$.region_name")

    @property
    def source(self):
        return self._get_attr_value("$.source")

    @property
    def isLongText(self):
        return self._get_attr_value("$.isLongText")

    @property
    def is_paid(self):
        return self._get_attr_value("$.is_paid")

    @property
    def is_public(self):
        return self._get_attr_value("$.title.text")

    @property
    def is_visible(self):
        return self._get_attr_value("$.visible.type")

    # user
    @property
    def user_id(self):
        return self._get_attr_value("$.user.idstr")

    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.user.screen_name"))

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserWeiboFilter(JSONModel):

    @property
    def status(self):
        return self._get_attr_value("$.ok")

    @property
    def message(self):
        return self._get_attr_value("$.message")

    @property
    def weibo_total(self):
        return self._get_attr_value("$.data.total")

    # Weibo
    @property
    def weibo_visible(self):
        return self._get_attr_value("$.data.list[*].visible.type")

    @property
    def weibo_created_at(self):
        return self._get_attr_value("$.data.list[*].created_at")

    @property
    def weibo_id(self):
        return self._get_attr_value("$.data.list[*].idstr")

    @property
    def weibo_isLongText(self):
        return self._get_attr_value("$.data.list[*].isLongText")

    @property
    def weibo_is_paid(self):
        return self._get_attr_value("$.data.list[*].is_paid")

    @property
    def weibo_mblogid(self):
        return self._get_attr_value("$.data.list[*].mblogid")

    @property
    def weibo_views(self):
        return self._get_attr_value(
            "$.data.list[*].number_display_strategy.display_text"
        )

    @property
    def weibo_digg_count(self):
        return self._get_attr_value("$.data.list[*].attitudes_count")

    @property
    def weibo_read_count(self):
        return self._get_attr_value("$.data.list[*].reads_count")

    @property
    def weibo_pic_ids(self):
        return self._get_attr_value("$.data.list[*].pic_ids")

    @property
    def weibo_pic_num(self):
        return self._get_attr_value("$.data.list[*].pic_num")

    @property
    def weibo_location(self):
        return self._get_attr_value("$.data.list[*].region_name")

    @property
    def weibo_reposts_count(self):
        return self._get_attr_value("$.data.list[*].reposts_count")

    @property
    def weibo_showFeedComment(self):
        return self._get_attr_value("$.data.list[*].showFeedComment")

    @property
    def weibo_showFeedRepost(self):
        return self._get_attr_value("$.data.list[*].showFeedRepost")

    @property
    def weibo_showPictureViewer(self):
        return self._get_attr_value("$.data.list[*].showPictureViewer")

    @property
    def weibo_desc(self):
        return replaceT(self._get_attr_value("$.data.list[*].text_raw"))

    @property
    def weibo_desc_raw(self):
        return self._get_attr_value("$.data.list[*].text_raw")

    @property
    def weibo_sorce(self):
        return self._get_attr_value("$.data.list[*].source")

    # 需要用#包裹并quote
    @property
    def weibo_topic_title(self):
        return self._get_attr_value("$.data.list[*].topic_struct[*].topic_title")

    # User
    @property
    def weibo_user_name(self):
        return replaceT(self._get_attr_value("$.data.list[*].user.screen_name"))

    @property
    def weibo_user_name_raw(self):
        return self._get_attr_value("$.data.list[*].user.screen_name")

    @property
    def weibo_user_uid(self):
        return self._get_attr_value("$.data.list[*].user.idstr")

    @property
    def weibo_user_domain(self):
        return self._get_attr_value("$.data.list[*].user.domain")

    @property
    def weibo_user_avatar_hd(self):
        return self._get_attr_value("$.data.list[*].user.avatar_hd")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }
