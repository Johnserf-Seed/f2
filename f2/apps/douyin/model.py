# path: f2/apps/douyin/models.py

from typing import Any
from pydantic import BaseModel
from urllib.parse import quote, unquote

from f2.apps.douyin.utils import TokenManager, VerifyFpManager, ClientConfManager


# Base Model
class BaseRequestModel(BaseModel):
    device_platform: str = "webapp"
    aid: str = "6383"
    channel: str = "channel_pc_web"
    pc_client_type: int = 1
    publish_video_strategy_type: int = 2
    pc_libra_divert: str = "Windows"
    version_code: str = ClientConfManager.brm_version().get("code", "290100")
    version_name: str = ClientConfManager.brm_version().get("name", "29.1.0")
    cookie_enabled: str = "true"
    screen_width: int = 1920
    screen_height: int = 1080
    browser_language: str = ClientConfManager.brm_browser().get("language", "zh-CN")
    browser_platform: str = ClientConfManager.brm_browser().get("platform", "Win32")
    browser_name: str = ClientConfManager.brm_browser().get("name", "Edge")
    browser_version: str = ClientConfManager.brm_browser().get("version", "130.0.0.0")
    browser_online: str = "true"
    engine_name: str = ClientConfManager.brm_engine().get("name", "Blink")
    engine_version: str = ClientConfManager.brm_engine().get("version", "130.0.0.0")
    os_name: str = ClientConfManager.brm_os().get("name", "Windows")
    os_version: str = ClientConfManager.brm_os().get("version", "10")
    cpu_core_num: int = 12
    device_memory: int = 8
    platform: str = "PC"
    downlink: int = 10
    effective_type: str = "4g"
    round_trip_time: int = 100
    try:
        msToken: str = TokenManager.gen_real_msToken()
    except:
        msToken: str = TokenManager.gen_real_msToken()


class BaseLiveModel(BaseModel):
    aid: str = "6383"
    app_name: str = "douyin_web"
    live_id: int = 1
    device_platform: str = "web"
    language: str = ClientConfManager.blm_language()
    cookie_enabled: str = "true"
    screen_width: int = 1920
    screen_height: int = 1080
    browser_language: str = ClientConfManager.blm_browser().get("language", "zh-CN")
    browser_platform: str = ClientConfManager.blm_browser().get("platform", "Win32")
    browser_name: str = ClientConfManager.blm_browser().get("name", "Edge")
    browser_version: str = ClientConfManager.blm_browser().get("version", "130.0.0.0")
    enter_source: Any = ""
    is_need_double_stream: str = "false"
    # msToken: str = TokenManager.gen_real_msToken()


class BaseLiveModel2(BaseModel):
    verifyFp: str = VerifyFpManager.gen_verify_fp()
    type_id: str = "0"
    live_id: str = "1"
    sec_user_id: str = ""
    version_code: str = "99.99.99"
    app_id: str = "1128"
    msToken: str = ""


class BaseLoginModel(BaseModel):
    service: str = "https://www.douyin.com"
    need_logo: str = "false"
    need_short_url: str = "true"
    device_platform: str = "web_app"
    aid: str = "6383"
    account_sdk_source: str = "sso"
    sdk_version: str = "2.2.7-beta.6"
    language: str = "zh"


class BaseWebCastModel(BaseModel):
    app_name: str = "douyin_web"
    version_code: str = "180800"
    device_platform: str = "web"
    cookie_enabled: str = "true"
    screen_width: int = 1920
    screen_height: int = 1080
    browser_language: str = "zh-CN"
    browser_platform: str = "Win32"
    browser_name: str = "Mozilla"
    browser_version: str = quote(
        "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        safe="",
    )
    browser_online: str = "true"
    tz_name: str = "Asia/Hong_Kong"
    host: str = "https://live.douyin.com"
    aid: int = 6383
    live_id: int = 1
    did_rule: int = 3
    endpoint: str = "live_pc"
    support_wrds: int = 1
    identity: str = "audience"
    need_persist_msg_count: int = 15
    insert_task_id: Any = ""
    live_reason: Any = ""


# Model
class UserProfile(BaseRequestModel):
    sec_user_id: str


class UserPost(BaseRequestModel):
    max_cursor: int
    count: int
    sec_user_id: str


class UserLike(BaseRequestModel):
    max_cursor: int
    count: int
    sec_user_id: str


class UserCollection(BaseRequestModel):
    # POST
    cursor: int
    count: int


class UserCollects(BaseRequestModel):
    # GET
    cursor: int
    count: int


class UserCollectsVideo(BaseRequestModel):
    # GET
    cursor: int
    count: int
    collects_id: str


class UserMusicCollection(BaseRequestModel):
    # GET
    cursor: int
    count: int


class UserMix(BaseRequestModel):
    cursor: int
    count: int
    mix_id: str


class FriendFeed(BaseRequestModel):
    cursor: int = 0
    level: int = 1
    aweme_ids: str = ""
    room_ids: str = ""
    pull_type: int = 0
    refresh_type: int = 0
    address_book_access: int = 2
    gps_access: int = 2
    recent_gids: str = ""


class PostFeed(BaseRequestModel):
    count: int = 10
    tag_id: str = ""
    share_aweme_id: str = ""
    live_insert_type: str = ""
    refresh_index: int = 1
    video_type_select: int = 1
    aweme_pc_rec_raw_data: dict = {}  # {"is_client":false}
    globalwid: str = ""
    pull_type: str = ""
    min_window: str = ""
    free_right: str = ""
    ug_source: str = ""
    creative_id: str = ""


class FollowFeed(BaseRequestModel):
    cursor: int = 0
    level: int = 1
    count: int = 20
    pull_type: str = ""


class PostRelated(BaseRequestModel):
    aweme_id: str
    count: int = 20
    filterGids: str  # id,id,id
    awemePcRecRawData: str = quote('{"is_client":false}', safe="")
    sub_channel_id: int = 3
    # Seo-Flag: int = 0


class PostDetail(BaseRequestModel):
    aweme_id: str


class PostComment(BaseRequestModel):
    aweme_id: str
    cursor: int = 0
    count: int = 20
    item_type: int = 0
    insert_ids: str
    whale_cut_token: str
    cut_version: int = 1
    rcFT: str


class PostLocate(BaseRequestModel):
    sec_user_id: str
    max_cursor: str  # last max_cursor
    locate_item_id: str = ""  # aweme_id
    locate_item_cursor: str
    locate_query: str = "true"
    count: int = 10
    publish_video_strategy_type: int = 2


class UserLive(BaseLiveModel):
    web_rid: str
    room_id_str: str


class UserLive2(BaseLiveModel2):
    room_id: str


class FollowingUserLive(BaseRequestModel):
    scene: str = "aweme_pc_follow_top"


class SuggestWord(BaseRequestModel):
    query: str = ""
    count: int = 8
    business_id: str
    from_group_id: str
    rsp_source: str = ""
    penetrate_params: dict = {}


class PostSearch(BaseRequestModel):
    search_channel: str = "aweme_general"
    filter_selected: str
    keyword: str
    search_source: str = "normal_search"
    # search_sug # tab_search # normal_search # guide_search # hot_search_board
    search_id: str = ""
    query_correct_type: int = 1
    is_filter_search: int = 0
    from_group_id: str = ""
    offset: int = 0
    count: int = 15
    need_filter_settings: int = 1


class LoginGetQr(BaseLoginModel):
    verifyFp: str = ""
    fp: str = ""
    # msToken: str = TokenManager.gen_real_msToken()


class LoginCheckQr(BaseLoginModel):
    token: str = ""
    verifyFp: str = ""
    fp: str = ""
    # msToken: str = TokenManager.gen_real_msToken()


class UserFollowing(BaseRequestModel):
    user_id: str = ""
    sec_user_id: str = ""
    offset: int = 0  # 相当于cursor
    min_time: int = 0
    max_time: int = 0
    count: int = 20
    # source_type = 1: 最近关注 需要指定max_time(s) 3: 最早关注 需要指定min_time(s) 4: 综合排序
    source_type: int = 4
    gps_access: int = 0
    address_book_access: int = 0
    is_top: int = 1


class UserFollower(BaseRequestModel):
    user_id: str
    sec_user_id: str
    offset: int = 0  # 相当于cursor 但只对source_type: = 2 有效，其他情况为 0 即可
    min_time: int = 0
    max_time: int = 0
    count: int = 20
    # source_type = 1: 最近关注 需要指定max_time(s) 2: 综合关注(意义不明)
    source_type: int = 1
    gps_access: int = 0
    address_book_access: int = 0
    is_top: int = 1


class LiveWebcast(BaseWebCastModel):
    webcast_sdk_version: str = "1.0.14-beta.0"
    update_version_code: str = "1.0.14-beta.0"
    compress: str = "gzip"
    im_path: str = "/webcast/im/fetch/"
    heartbeatDuration: int = 0
    room_id: str
    user_unique_id: str
    cursor: str
    internal_ext: str
    signature: str  # 暂时调用execjs，纯算还在扣


class LiveImFetch(BaseWebCastModel):
    # resp_content_type: str = "protobuf"
    resp_content_type: str = "json"
    fetch_rule: int = 1
    last_rtt: int = 0
    cursor: str = ""
    internal_ext: str = ""
    room_id: str
    user_unique_id: str


class QueryUser(BaseRequestModel):
    publish_video_strategy_type: int = 2
    update_version_code: str = "170400"
    version_code: str = "170400"
    version_name: str = "17.4.0"


class PostStats(BaseRequestModel):
    aweme_type: int
    item_id: str
    play_delta: int = 1
    source: int = 0
