# path: f2/apps/tiktok/filter.py

from f2.utils.json_filter import JSONModel
from f2.utils.utils import _get_first_item_from_list, timestamp_2_str, replaceT


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
    def commentSetting(self) -> bool:
        return bool(self._get_attr_value("$.userInfo.user.commentSetting"))

    @property
    def followingVisibility(self) -> bool:
        return bool(self._get_attr_value("$.userInfo.user.followingVisibility"))

    @property
    def openFavorite(self) -> bool:
        return bool(self._get_attr_value("$.userInfo.user.openFavorite"))

    @property
    def privateAccount(self) -> bool:
        return bool(self._get_attr_value("$.userInfo.user.privateAccount"))

    @property
    def showPlayListTab(self) -> bool:
        return bool(self._get_attr_value("$.userInfo.user.profileTab.showPlayListTab"))

    @property
    def relation(self) -> bool:  # follow 1, no follow 0
        return bool(self._get_attr_value("$.userInfo.user.relation"))

    @property
    def signature(self):
        return replaceT(self._get_attr_value("$.userInfo.user.signature"))

    @property
    def signature_raw(self):
        return self._get_attr_value("$.userInfo.user.signature")

    @property
    def ttSeller(self) -> bool:
        return bool(self._get_attr_value("$.userInfo.user.ttSeller"))

    @property
    def verified(self) -> bool:
        return bool(self._get_attr_value("$.userInfo.user.verified"))

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
            [aweme.get("Bitrate", "")]  # 使用 get 方法以处理字典中没有 "Bitrate" 键的情况
            if isinstance(aweme, dict)
            else [aweme[0].get("Bitrate", "")]
            if len(aweme) == 1
            else [item.get("Bitrate", "") for item in aweme]
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

    def _to_list(self):
        # 定义不需要的属性列表
        exclude_list = ["hasMore", "cursor", "has_aweme", "api_status_code"]
        # 生成属性名称列表，然后过滤掉不需要的属性
        keys = [
            prop_name
            for prop_name in dir(self)
            if not prop_name.startswith("__")
            and not prop_name.startswith("_")
            and prop_name not in exclude_list
        ]

        aweme_entries = self._get_attr_value("$.itemList") or []

        list_dicts = []
        # 遍历每个条目并创建一个字典
        # (Iterate through each entry and create a dict)
        for entry in aweme_entries:
            d = {"hasMore": self.hasMore, "cursor": self.cursor}
            for key in keys:
                attr_values = getattr(self, key)
                # 当前aweme_entry在属性列表中的索引
                index = aweme_entries.index(entry)
                # 如果属性值的长度足够则赋值，否则赋None
                # (Assign value if the length of the attribute value is sufficient, otherwise assign None)
                d[key] = attr_values[index] if index < len(attr_values) else None
            list_dicts.append(d)
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
    def collected(self) -> bool:
        return bool(self._get_attr_value("$.itemInfo.itemStruct.collected"))

    @property
    def digged(self) -> bool:
        return bool(self._get_attr_value("$.itemInfo.itemStruct.digged"))

    @property
    def forFriend(self) -> bool:
        return bool(self._get_attr_value("$.itemInfo.itemStruct.forFriend"))

    @property
    def itemCommentStatus(self) -> bool:
        return bool(self._get_attr_value("$.itemInfo.itemStruct.itemCommentStatus"))

    @property
    def privateItem(self) -> bool:
        return bool(self._get_attr_value("$.itemInfo.itemStruct.privateItem"))

    @property
    def secret(self) -> bool:
        return bool(self._get_attr_value("$.itemInfo.itemStruct.secret"))

    @property
    def shareEnabled(self) -> bool:
        return bool(self._get_attr_value("$.itemInfo.itemStruct.shareEnabled"))

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

    def _to_list(self):
        exclude_list = []
        keys = [
            prop_name
            for prop_name in dir(self)
            if not prop_name.startswith("__")
            and not prop_name.startswith("_")
            and prop_name not in exclude_list
        ]
        aweme_entries = self._get_attr_value("$.itemInfo.itemStruct") or []
        list_dicts = []

        for entry in aweme_entries:
            d = {}
            for key in keys:
                attr_values = getattr(self, key, [])
                index = aweme_entries.index(entry)
                d[key] = attr_values[index] if index < len(attr_values) else None
            list_dicts.append(d)
        return list_dicts
