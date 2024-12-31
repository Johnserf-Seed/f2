# path: f2/apps/tiktok/filter.py

from f2.utils.json_filter import JSONModel
from f2.utils.utils import timestamp_2_str, replaceT, unescape_json, filter_to_list


class UserProfileFilter(JSONModel):
    @property
    def api_status_code(self):
        return self._get_attr_value("$.statusCode")

    # stats
    @property
    def diggCount(self):
        return self._get_attr_value("$.userInfo.stats.diggCount")

    @property
    def followerCount(self):
        return self._get_attr_value("$.userInfo.stats.followerCount")

    @property
    def followingCount(self):
        return self._get_attr_value("$.userInfo.stats.followingCount")

    @property
    def friendCount(self):
        return self._get_attr_value("$.userInfo.stats.friendCount")

    @property
    def heartCount(self):
        return self._get_attr_value("$.userInfo.stats.heartCount")

    @property
    def videoCount(self):
        return self._get_attr_value("$.userInfo.stats.videoCount")

    # user
    @property
    def uid(self):
        return self._get_attr_value("$.userInfo.user.id")

    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.userInfo.user.nickname"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.userInfo.user.nickname")

    @property
    def secUid(self):
        return self._get_attr_value("$.userInfo.user.secUid")

    @property
    def uniqueId(self):
        return self._get_attr_value("$.userInfo.user.uniqueId")

    @property
    def commentSetting(self):
        return self._get_attr_value("$.userInfo.user.commentSetting")

    @property
    def followingVisibility(self):
        return self._get_attr_value("$.userInfo.user.followingVisibility")

    @property
    def openFavorite(self):
        return self._get_attr_value("$.userInfo.user.openFavorite")

    @property
    def privateAccount(self):
        return self._get_attr_value("$.userInfo.user.privateAccount")

    @property
    def showPlayListTab(self):
        return self._get_attr_value("$.userInfo.user.profileTab.showPlayListTab")

    @property
    def relation(self):  # follow 1, no follow 0
        return self._get_attr_value("$.userInfo.user.relation")

    @property
    def signature(self):
        return replaceT(self._get_attr_value("$.userInfo.user.signature"))

    @property
    def signature_raw(self):
        return self._get_attr_value("$.userInfo.user.signature")

    @property
    def ttSeller(self):
        return self._get_attr_value("$.userInfo.user.ttSeller")

    @property
    def verified(self):
        return self._get_attr_value("$.userInfo.user.verified")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class UserPostFilter(JSONModel):
    @property
    def api_status_code(self):
        return self._get_attr_value("$.statusCode")

    @property
    def has_aweme(self) -> bool:
        return bool(self._get_attr_value("$.itemList"))

    @property
    def hasMore(self) -> bool:
        return bool(self._get_attr_value("$.hasMore"))

    @property
    def cursor(self):
        return self._get_attr_value("$.cursor")

    @property
    def aweme_id(self):
        ids = self._get_list_attr_value("$.itemList[*].id")
        return ids if isinstance(ids, list) else [ids]

    @property
    def createTime(self):
        create_times = self._get_list_attr_value("$.itemList[*].createTime")
        return (
            [timestamp_2_str(ct) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(create_times)
        )

    @property
    def desc(self):
        return replaceT(self._get_list_attr_value("$.itemList[*].desc"))

    @property
    def desc_raw(self):
        return self._get_list_attr_value("$.itemList[*].desc")

    @property
    def textExtra(self):
        return self._get_list_attr_value("$.itemList[*].textExtra")

    # author

    @property
    def nickname(self):
        return replaceT(self._get_list_attr_value("$.itemList[*].author.nickname"))

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.itemList[*].author.nickname")

    @property
    def uid(self):
        return self._get_list_attr_value("$.itemList[*].author.id")

    @property
    def secUid(self):
        return self._get_list_attr_value("$.itemList[*].author.secUid")

    # your stats
    @property
    def collected(self):
        return self._get_list_attr_value("$.itemList[*].collected")

    @property
    def digged(self):
        return self._get_list_attr_value("$.itemList[*].digged")

    @property
    def duetDisplay(self):
        return self._get_list_attr_value("$.itemList[*].duetDisplay")

    @property
    def duetEnabled(self):
        return self._get_list_attr_value("$.itemList[*].duetEnabled")

    @property
    def forFriend(self):
        return self._get_list_attr_value("$.itemList[*].forFriend")

    @property
    def isPinnedItem(self):
        return self._get_list_attr_value("$.itemList[*].isPinnedItem")

    @property
    def itemCommentStatus(self):
        return self._get_list_attr_value("$.itemList[*].itemCommentStatus")

    @property
    def privateItem(self):
        return self._get_list_attr_value("$.itemList[*].privateItem")

    @property
    def secret(self):
        return self._get_list_attr_value("$.itemList[*].secret")

    @property
    def shareEnabled(self):
        return self._get_list_attr_value("$.itemList[*].shareEnabled")

    # aweme stats
    @property
    def collectCount(self):
        return self._get_list_attr_value("$.itemList[*].stats.collectCount")

    @property
    def commentCount(self):
        return self._get_list_attr_value("$.itemList[*].stats.commentCount")

    @property
    def diggCount(self):
        return self._get_list_attr_value("$.itemList[*].stats.diggCount")

    @property
    def playCount(self):
        return self._get_list_attr_value("$.itemList[*].stats.playCount")

    @property
    def shareCount(self):
        return self._get_list_attr_value("$.itemList[*].stats.shareCount")

    # music
    @property
    def music_album(self):
        return self._get_list_attr_value("$.itemList[*].music.album")

    @property
    def music_authorName(self):
        return replaceT(self._get_list_attr_value("$.itemList[*].music.authorName"))

    @property
    def music_authorName_raw(self):
        return self._get_list_attr_value("$.itemList[*].music.authorName")

    @property
    def music_coverLarge(self):
        return self._get_list_attr_value("$.itemList[*].music.coverLarge")

    @property
    def music_duration(self):
        return self._get_list_attr_value("$.itemList[*].music.duration")

    @property
    def music_id(self):
        return self._get_list_attr_value("$.itemList[*].music.id")

    @property
    def music_original(self):
        return self._get_list_attr_value("$.itemList[*].music.original")

    @property
    def music_playUrl(self):
        return self._get_list_attr_value("$.itemList[*].music.playUrl")

    @property
    def music_title(self):
        return replaceT(self._get_list_attr_value("$.itemList[*].music.title"))

    @property
    def music_title_raw(self):
        return self._get_list_attr_value("$.itemList[*].music.title")

    # video
    @property
    def video_bitrate(self):
        return self._get_list_attr_value("$.itemList[*].video.bitrate")

    # @property
    # def video_bitrateInfo(self):
    #     bit_rate_data = self._get_list_attr_value("$.itemList[*].video.bitrateInfo")
    #     return [
    #         [aweme["Bitrate"]]
    #         if isinstance(aweme, dict)
    #         else [aweme[0]["Bitrate"]]
    #         if len(aweme) == 1
    #         else [item["Bitrate"] for item in aweme]
    #         for aweme in bit_rate_data
    #     ]

    @property
    def video_bitrateInfo(self):
        bit_rate_data = self._get_list_attr_value("$.itemList[*].video.bitrateInfo")
        return [
            (
                (
                    [aweme.get("Bitrate", "")]  # 如果 aweme 是字典，获取 "Bitrate"
                    if isinstance(aweme, dict)
                    else (
                        [
                            aweme[0].get("Bitrate", "")
                        ]  # 如果 aweme 是单元素列表，获取第一个元素的 "Bitrate"
                        if isinstance(aweme, list) and len(aweme) == 1
                        else (
                            [
                                item.get("Bitrate", "") for item in aweme
                            ]  # 如果 aweme 是多元素列表，遍历获取每个元素的 "Bitrate"
                            if isinstance(aweme, list)
                            else []
                        )
                    )
                )
                if aweme is not None
                else []
            )  # 如果 aweme 是 None，返回空列表
            for aweme in bit_rate_data
        ]

    @property
    def video_codecType(self):
        return self._get_list_attr_value("$.itemList[*].video.codecType")

    @property
    def video_cover(self):
        return self._get_list_attr_value("$.itemList[*].video.cover")

    @property
    def video_dynamicCover(self):
        return self._get_list_attr_value("$.itemList[*].video.dynamicCover")

    @property
    def video_playAddr(self):
        return self._get_list_attr_value("$.itemList[*].video.playAddr")

    @property
    def video_definition(self):
        return self._get_list_attr_value("$.itemList[*].video.definition")

    @property
    def video_duration(self):
        return self._get_list_attr_value("$.itemList[*].video.duration")

    @property
    def video_height(self):
        return self._get_list_attr_value("$.itemList[*].video.height")

    @property
    def video_width(self):
        return self._get_list_attr_value("$.itemList[*].video.width")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        # 定义不需要的属性列表
        exclude_fields = [
            "hasMore",
            "cursor",
            "has_aweme",
            "api_status_code",
        ]
        extra_fields = [
            "hasMore",
            "cursor",
        ]

        list_dicts = filter_to_list(
            self,
            "$.itemList",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class UserCollectFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)


class UserMixFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)


class UserLikeFilter(UserPostFilter):
    def __init__(self, data):
        super().__init__(data)


class UserPlayListFilter(JSONModel):
    @property
    def api_status_code(self):
        return self._get_attr_value("$.statusCode")

    @property
    def hasPlayList(self) -> bool:
        return bool(self._get_attr_value("$.playList"))

    @property
    def hasMore(self) -> bool:
        return bool(self._get_attr_value("$.hasMore"))

    @property
    def mixId(self):
        return self._get_attr_value("$.playList[*].mixId")

    @property
    def mixName(self):
        return self._get_attr_value("$.playList[*].mixName")

    @property
    def videoCount(self):
        return self._get_attr_value("$.playList[*].videoCount")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class PostDetailFilter(JSONModel):
    @property
    def api_status_code(self):
        return self._get_attr_value("$.statusCode")

    # author
    @property
    def author_avatarLarger(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.avatarLarger")

    @property
    def commentSetting(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.commentSetting")

    @property
    def downloadSetting(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.downloadSetting")

    @property
    def uid(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.id")

    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.itemInfo.itemStruct.author.nickname"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.nickname")

    @property
    def secUid(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.secUid")

    @property
    def uniqueId(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.uniqueId")

    @property
    def signature(self):
        return replaceT(self._get_attr_value("$.itemInfo.itemStruct.author.signature"))

    @property
    def signature_raw(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.signature")

    @property
    def openFavorite(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.openFavorite")

    @property
    def privateAccount(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.privateAccount")

    @property
    def verified(self):
        return self._get_attr_value("$.itemInfo.itemStruct.author.verified")

    # challenges
    @property
    def challenges_title(self):
        return self._get_attr_value("$.itemInfo.itemStruct.challenges[*].title")

    @property
    def challenges_desc(self):
        return self._get_attr_value("$.itemInfo.itemStruct.challenges[*].desc")

    # aweme
    @property
    def createTime(self):
        return timestamp_2_str(
            str(self._get_attr_value("$.itemInfo.itemStruct.createTime"))
        )

    @property
    def desc(self):
        return replaceT(self._get_attr_value("$.itemInfo.itemStruct.desc"))

    @property
    def desc_raw(self):
        return self._get_attr_value("$.itemInfo.itemStruct.desc")

    @property
    def textExtra(self):
        return self._get_attr_value("$.itemInfo.itemStruct.textExtra")

    @property
    def aweme_id(self):
        return self._get_attr_value("$.itemInfo.itemStruct.id")

    # aweme stats
    @property
    def collected(self):
        return self._get_attr_value("$.itemInfo.itemStruct.collected")

    @property
    def digged(self):
        return self._get_attr_value("$.itemInfo.itemStruct.digged")

    @property
    def forFriend(self):
        return self._get_attr_value("$.itemInfo.itemStruct.forFriend")

    @property
    def itemCommentStatus(self):
        return self._get_attr_value("$.itemInfo.itemStruct.itemCommentStatus")

    @property
    def privateItem(self):
        return self._get_attr_value("$.itemInfo.itemStruct.privateItem")

    @property
    def secret(self):
        return self._get_attr_value("$.itemInfo.itemStruct.secret")

    @property
    def shareEnabled(self):
        return self._get_attr_value("$.itemInfo.itemStruct.shareEnabled")

    # stats
    @property
    def commentCount(self):
        return self._get_attr_value("$.itemInfo.itemStruct.stats.commentCount")

    @property
    def diggCount(self):
        return self._get_attr_value("$.itemInfo.itemStruct.stats.diggCount")

    @property
    def playCount(self):
        return self._get_attr_value("$.itemInfo.itemStruct.stats.playCount")

    @property
    def shareCount(self):
        return self._get_attr_value("$.itemInfo.itemStruct.stats.shareCount")

    # suggestedWords
    @property
    def suggestedWords(self):
        return self._get_attr_value("$.itemInfo.itemStruct.suggestedWords")

    @property
    def videoSuggestWordsList(self):
        return self._get_attr_value(
            "$.itemInfo.itemStruct.videoSuggestWordsList.video_suggest_words_struct"
        )

    # music
    @property
    def music_authorName(self):
        return replaceT(self._get_attr_value("$.itemInfo.itemStruct.music.authorName"))

    @property
    def music_authorName_raw(self):
        return self._get_attr_value("$.itemInfo.itemStruct.music.authorName")

    @property
    def music_coverLarge(self):
        return self._get_attr_value("$.itemInfo.itemStruct.music.coverLarge")

    @property
    def music_duration(self):
        return self._get_attr_value("$.itemInfo.itemStruct.music.duration")

    @property
    def music_id(self):
        return self._get_attr_value("$.itemInfo.itemStruct.music.id")

    @property
    def music_original(self):
        return self._get_attr_value("$.itemInfo.itemStruct.music.original")

    @property
    def music_playUrl(self):
        return self._get_attr_value("$.itemInfo.itemStruct.music.playUrl")

    @property
    def music_title(self):
        return replaceT(self._get_attr_value("$.itemInfo.itemStruct.music.title"))

    @property
    def music_title_raw(self):
        return self._get_attr_value("$.itemInfo.itemStruct.music.title")

    # video
    @property
    def video_bitrate(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.bitrate")

    @property
    def video_bitrateInfo(self):
        bit_rate_data = self._get_attr_value("$.itemInfo.itemStruct.video.bitrateInfo")
        if bit_rate_data is None:
            return []  # 或者根据实际需求返回其他默认值
        return [item["Bitrate"] for item in bit_rate_data]

    @property
    def video_codecType(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.codecType")

    @property
    def video_cover(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.cover")

    @property
    def video_dynamicCover(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.dynamicCover")

    @property
    def video_playAddr(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.playAddr")

    @property
    def video_definition(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.definition")

    @property
    def video_duration(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.duration")

    @property
    def video_height(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.height")

    @property
    def video_width(self):
        return self._get_attr_value("$.itemInfo.itemStruct.video.width")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields = []
        extra_fields = []

        list_dicts = filter_to_list(
            self,
            "$.itemInfo.itemStruct",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class PostSearchFilter(JSONModel):
    @property
    def api_status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def has_aweme(self) -> bool:
        return bool(self._get_attr_value("$.item_list"))

    @property
    def has_more(self) -> bool:
        return bool(self._get_attr_value("$.has_more"))

    @property
    def cursor(self):
        return self._get_attr_value("$.cursor")

    @property
    def backtrace(self):
        return self._get_attr_value("$.backtrace")

    @property
    def search_id(self):
        return self._get_attr_value("$.extra.logid")

    @property
    def aweme_id(self):
        ids = self._get_list_attr_value("$.item_list[*].id")
        return ids if isinstance(ids, list) else [ids]

    @property
    def createTime(self):
        create_times = self._get_list_attr_value("$.item_list[*].createTime")
        return (
            [timestamp_2_str(ct) for ct in create_times]
            if isinstance(create_times, list)
            else timestamp_2_str(create_times)
        )

    @property
    def desc(self):
        return replaceT(self._get_list_attr_value("$.item_list[*].desc"))

    @property
    def desc_raw(self):
        return self._get_list_attr_value("$.item_list[*].desc")

    @property
    def textExtra(self):
        return self._get_list_attr_value("$.item_list[*].textExtra")

    # music
    @property
    def music_album(self):
        return self._get_list_attr_value("$.item_list[*].music.album")

    @property
    def music_authorName(self):
        return replaceT(self._get_list_attr_value("$.item_list[*].music.authorName"))

    @property
    def music_authorName_raw(self):
        return self._get_list_attr_value("$.item_list[*].music.authorName")

    @property
    def music_coverLarge(self):
        return self._get_list_attr_value("$.item_list[*].music.coverLarge")

    @property
    def music_duration(self):
        return self._get_list_attr_value("$.item_list[*].music.duration")

    @property
    def music_id(self):
        return self._get_list_attr_value("$.item_list[*].music.id")

    @property
    def music_original(self):
        return self._get_list_attr_value("$.item_list[*].music.original")

    @property
    def music_playUrl(self):
        return self._get_list_attr_value("$.item_list[*].music.playUrl")

    @property
    def music_title(self):
        return replaceT(self._get_list_attr_value("$.item_list[*].music.title"))

    @property
    def music_title_raw(self):
        return self._get_list_attr_value("$.item_list[*].music.title")

    # video
    @property
    def video_bitrate(self):
        return self._get_list_attr_value("$.item_list[*].video.bitrate")

    @property
    def video_codecType(self):
        return self._get_list_attr_value("$.item_list[*].video.codecType")

    @property
    def video_cover(self):
        return self._get_list_attr_value("$.item_list[*].video.cover")

    @property
    def video_dynamicCover(self):
        return self._get_list_attr_value("$.item_list[*].video.dynamicCover")

    @property
    def video_playAddr(self):
        return self._get_list_attr_value("$.item_list[*].video.playAddr")

    @property
    def video_duration(self):
        return self._get_list_attr_value("$.item_list[*].video.duration")

    @property
    def video_height(self):
        return self._get_list_attr_value("$.item_list[*].video.height")

    @property
    def video_width(self):
        return self._get_list_attr_value("$.item_list[*].video.width")

    # author
    @property
    def nickname(self):
        return replaceT(self._get_list_attr_value("$.item_list[*].author.nickname"))

    @property
    def nickname_raw(self):
        return self._get_list_attr_value("$.item_list[*].author.nickname")

    @property
    def uid(self):
        return self._get_list_attr_value("$.item_list[*].author.id")

    @property
    def secUid(self):
        return self._get_list_attr_value("$.item_list[*].author.secUid")

    # your stats
    @property
    def collected(self):
        return self._get_list_attr_value("$.item_list[*].collected")

    @property
    def digged(self):
        return self._get_list_attr_value("$.item_list[*].digged")

    @property
    def duetEnabled(self):
        return self._get_list_attr_value("$.item_list[*].duetEnabled")

    @property
    def forFriend(self):
        return self._get_list_attr_value("$.item_list[*].forFriend")

    @property
    def itemCommentStatus(self):
        return self._get_list_attr_value("$.item_list[*].itemCommentStatus")

    @property
    def privateItem(self):
        return self._get_list_attr_value("$.item_list[*].privateItem")

    @property
    def secret(self):
        return self._get_list_attr_value("$.item_list[*].secret")

    @property
    def shareEnabled(self):
        return self._get_list_attr_value("$.item_list[*].shareEnabled")

    # aweme stats
    @property
    def collectCount(self):
        return self._get_list_attr_value("$.item_list[*].stats.collectCount")

    @property
    def commentCount(self):
        return self._get_list_attr_value("$.item_list[*].stats.commentCount")

    @property
    def diggCount(self):
        return self._get_list_attr_value("$.item_list[*].stats.diggCount")

    @property
    def playCount(self):
        return self._get_list_attr_value("$.item_list[*].stats.playCount")

    @property
    def shareCount(self):
        return self._get_list_attr_value("$.item_list[*].stats.shareCount")

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
            "has_more",
            "cursor",
            "has_aweme",
            "api_status_code",
        ]
        extra_fields = [
            "has_more",
            "cursor",
        ]

        list_dicts = filter_to_list(
            self,
            "$.item_list",
            exclude_fields,
            extra_fields,
        )

        return list_dicts


class UserLiveFilter(JSONModel):
    @property
    def api_status_code(self):
        return self._get_attr_value("$.statusCode")

    @property
    def has_live(self) -> bool:
        data = self._get_attr_value("$.data")
        return bool(data) and len(data) != 4

    # user
    @property
    def user_avatar_larger(self):
        return self._get_attr_value("$.data.user.avatarLarger")

    @property
    def user_id(self):
        return self._get_attr_value("$.data.user.id")

    @property
    def nickname(self):
        return replaceT(self._get_attr_value("$.data.user.nickname"))

    @property
    def nickname_raw(self):
        return self._get_attr_value("$.data.user.nickname")

    @property
    def user_secUid(self):
        return self._get_attr_value("$.data.user.secUid")

    @property
    def user_uniqueId(self):
        return self._get_attr_value("$.data.user.uniqueId")

    @property
    def user_secret(self):
        return self._get_attr_value("$.data.user.secret")

    @property
    def user_verified(self):
        return self._get_attr_value("$.data.user.verified")

    @property
    def user_signature(self):
        return replaceT(self._get_attr_value("$.data.user.signature"))

    # stats
    @property
    def live_following_count(self):
        return self._get_attr_value("$.data.stats.followingCount")

    @property
    def live_follower_count(self):
        return self._get_attr_value("$.data.stats.followerCount")

    @property
    def live_user_count(self):
        return self._get_attr_value("$.data.liveRoom.liveRoomStats.userCount")

    # live
    @property
    def live_title(self):
        return replaceT(self._get_attr_value("$.data.liveRoom.title"))

    @property
    def live_title_raw(self):
        return self._get_attr_value("$.data.liveRoom.title")

    @property
    def live_startTime(self):
        return timestamp_2_str(self._get_attr_value("$.data.liveRoom.startTime"))

    @property
    def live_status(self):
        return self._get_attr_value("$.data.liveRoom.status")  # 2开播

    @property
    def live_coverUrl(self):
        return self._get_attr_value("$.data.liveRoom.coverUrl")

    @property
    def live_room_mode(self):
        return self._get_attr_value("$.data.liveRoom.mode")  # 0直播 1聊天室

    @property
    def live_room_id(self):
        return self._get_attr_value("$.data.user.roomId")

    @property
    def live_stream_id(self):
        return self._get_attr_value("$.data.liveRoom.streamId")

    @property
    def live_qualities(self):
        return self._get_list_attr_value(
            "$.data.liveRoom.streamData.pull_data.options.qualities[*].sdk_key"
        )

    @property
    def live_stream_data(self):
        return unescape_json(
            self._get_attr_value("$.data.liveRoom.streamData.pull_data.stream_data")
        )

    @property
    def live_flv_url(self):
        return JSONModel(self.live_stream_data)._get_attr_value(
            "$.data.origin.main.flv"
        )

    @property
    def live_hls_url(self):
        return JSONModel(self.live_stream_data)._get_attr_value(
            "$.data.origin.main.hls"
        )

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }


class CheckLiveAliveFilter(JSONModel):
    @property
    def api_status_code(self):
        return self._get_attr_value("$.status_code")

    @property
    def is_alive(self):
        return self._get_list_attr_value("$.data[*].alive")

    @property
    def room_id(self):
        return self._get_list_attr_value("$.data[*].room_id")

    def _to_raw(self) -> dict:
        return self._data

    def _to_dict(self) -> dict:
        return {
            prop_name: getattr(self, prop_name)
            for prop_name in dir(self)
            if not prop_name.startswith("__") and not prop_name.startswith("_")
        }

    def _to_list(self) -> list:
        exclude_fields = ["api_status_code"]
        extra_fields = []

        list_dicts = filter_to_list(
            self,
            "$.data",
            exclude_fields,
            extra_fields,
        )

        return list_dicts
