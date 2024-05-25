# path: f2/apps/tiktok/models.py

from typing import Any
from pydantic import BaseModel
from urllib.parse import quote, unquote

from f2.apps.tiktok.utils import TokenManager, ClientConfManager
from f2.utils.utils import get_timestamp


# Model
class BaseRequestModel(BaseModel):
    WebIdLastTime: str = str(get_timestamp("sec"))
    aid: str = "1988"
    app_language: str = "zh-Hans"
    app_name: str = "tiktok_web"
    browser_language: str = ClientConfManager.brm_browser().get("language", "zh-CN")
    browser_name: str = ClientConfManager.brm_browser().get("name", "Mozilla")
    browser_online: str = "true"
    browser_platform: str = ClientConfManager.brm_browser().get("platform", "Win32")
    browser_version: str = quote(
        ClientConfManager.brm_browser().get(
            "version",
            "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ),
        safe="",
    )
    channel: str = "tiktok_web"
    cookie_enabled: str = "true"
    device_id: str = ClientConfManager.brm_device().get(
        "id", "7372218823115949569"
    )  # 风控参数
    device_platform: str = ClientConfManager.brm_device().get("platform", "web_pc")
    focus_state: str = "true"
    from_page: str = "user"
    history_len: int = 4
    is_fullscreen: str = "false"
    is_page_visible: str = "true"
    language: str = "zh-Hans"
    os: str = ClientConfManager.base_request_model().get("os", "windows")
    priority_region: str = ClientConfManager.base_request_model().get(
        "priority_region", "US"
    )
    referer: str = ""
    region: str = ClientConfManager.base_request_model().get(
        "region", "SG"
    )  # SG JP KR...
    # root_referer: str = quote("https://www.tiktok.com/", safe="")
    screen_height: int = 1080
    screen_width: int = 1920
    webcast_language: str = ClientConfManager.base_request_model().get(
        "webcast_language", "zh-Hans"
    )
    tz_name: str = quote(
        ClientConfManager.base_request_model().get("tz_name", "Asia/Hong_Kong"), safe=""
    )
    try:
        msToken: str = TokenManager.gen_real_msToken()
    except Exception as e:
        print(f"Error generating msToken: {e}")
        # 发生异常时，重新生成msToken，不生成虚假msToken
        msToken: str = TokenManager.gen_real_msToken()


# router model
class UserProfile(BaseRequestModel):
    secUid: str
    uniqueId: str


class UserPost(BaseRequestModel):
    coverFormat: int = 2
    count: int = 35
    cursor: int = 0
    secUid: str


class UserLike(BaseRequestModel):
    coverFormat: int = 2
    count: int = 30
    cursor: int = 0
    secUid: str


class UserCollect(BaseRequestModel):
    coverFormat: int = 2
    count: int = 30
    cursor: int = 0
    secUid: str


class UserPlayList(BaseRequestModel):
    count: int = 30
    cursor: int = 0
    secUid: str


class UserMix(BaseRequestModel):
    count: int = 30
    cursor: int = 0
    mixId: str


class PostDetail(BaseRequestModel):
    itemId: str


class PostComment(BaseRequestModel):
    aweme_id: str
    count: int = 20
    cursor: int = 0
    current_region: str = ""


class PostSearch(BaseRequestModel):
    count: int = 20
    keyword: str
    offset: int = 0
    from_page: str = "search"
    search_id: str = ""
    web_search_code: str = quote(
        str(
            {
                "tiktok": {
                    "client_params_x": {
                        "search_engine": {
                            "ies_mt_user_live_video_card_use_libra": 1,
                            "mt_search_general_user_live_card": 1,
                        }
                    },
                    "search_server": {},
                }
            }
        ),
        safe="",
    )


class UserLive(BaseRequestModel):
    uniqueId: str
    sourceType: int = 54
