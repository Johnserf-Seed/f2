# path: tests/test_douyin_mix.py

from types import SimpleNamespace

import httpx
import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.apps.douyin.utils import MixIdFetcher
from f2.exceptions import APIConnectionError, APIResponseError

PLAYLET_ID = "7304153426445731880"
PLAYLET_URL = (
    f"https://www.iesdouyin.com/share/playlet/detail/{PLAYLET_ID}/"
    f"?schema_type=43&object_id={PLAYLET_ID}&from_ssr=1"
)


def forbid_request(self):
    raise AssertionError("地址里已经带有合集ID，不应发起请求")


def mock_redirect(monkeypatch, location):
    """短链接返回 302 跳转到 location，其余地址返回 200"""

    def handler(request):
        if request.url.host == "v.douyin.com":
            return httpx.Response(302, headers={"Location": location})
        return httpx.Response(200, text="ok")

    def init(self):
        self._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(MixIdFetcher, "__init__", init)


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://www.douyin.com/collection/7360898383181809676",
            "7360898383181809676",
        ),
        (
            "https://www.iesdouyin.com/share/mix/detail/7360898383181809676/?schema_type=24",
            "7360898383181809676",
        ),
        (PLAYLET_URL, PLAYLET_ID),
        (
            f"0.53 复制打开抖音，看看【于哲金的短剧】 {PLAYLET_URL} Mjc:/ 08/15",
            PLAYLET_ID,
        ),
    ],
)
async def test_get_mix_id_from_url_without_request(monkeypatch, url, expected):
    monkeypatch.setattr(MixIdFetcher, "__init__", forbid_request)
    assert await MixIdFetcher.get_mix_id(url) == expected


async def test_get_mix_id_follows_short_link_to_playlet(monkeypatch):
    # #423：合集短链现在跳转到短剧分享页
    mock_redirect(monkeypatch, PLAYLET_URL)
    assert (
        await MixIdFetcher.get_mix_id("https://v.douyin.com/jiHX9FuEqXE/") == PLAYLET_ID
    )


async def test_get_mix_id_rejects_non_mix_page(monkeypatch):
    mock_redirect(monkeypatch, "https://www.iesdouyin.com/share/user/MS4wLjABAAAA")
    with pytest.raises(APIResponseError):
        await MixIdFetcher.get_mix_id("https://v.douyin.com/xl_ZQix867A/")


def make_handler():
    return douyin_handler.DouyinHandler(
        {
            "url": "https://www.douyin.com/note/7686072587252833777",
            "cookie": "ttwid=guest",
            "headers": {"User-Agent": "f2-test"},
        }
    )


async def raise_not_mix(url):
    raise APIResponseError("未在响应的地址中找到mix_id")


async def test_mix_mode_reports_video_outside_any_mix(monkeypatch):
    async def get_aweme_id(url):
        return "7686072587252833777"

    async def fetch_one_video(self, aweme_id):
        return SimpleNamespace(mix_id=None, sec_user_id="MS4wLjABAAAA")

    monkeypatch.setattr(douyin_handler.MixIdFetcher, "get_mix_id", raise_not_mix)
    monkeypatch.setattr(douyin_handler.AwemeIdFetcher, "get_aweme_id", get_aweme_id)
    monkeypatch.setattr(
        douyin_handler.DouyinHandler, "fetch_one_video", fetch_one_video
    )

    with pytest.raises(APIResponseError, match="7686072587252833777"):
        await make_handler().handle_user_mix()


async def test_mix_mode_reports_empty_mix(monkeypatch):
    async def get_mix_id(url):
        return PLAYLET_ID

    async def fetch_user_mix_videos(self, mix_id, *args, **kwargs):
        yield SimpleNamespace(sec_user_id=[])

    monkeypatch.setattr(douyin_handler.MixIdFetcher, "get_mix_id", get_mix_id)
    monkeypatch.setattr(
        douyin_handler.DouyinHandler, "fetch_user_mix_videos", fetch_user_mix_videos
    )

    # 此前合集为空时 sec_user_id 未赋值，会抛出 UnboundLocalError
    with pytest.raises(APIResponseError, match=PLAYLET_ID):
        await make_handler().handle_user_mix()


async def test_mix_mode_does_not_fall_back_on_network_errors(monkeypatch):
    async def get_mix_id(url):
        raise APIConnectionError("网络连接失败")

    async def get_aweme_id(url):
        raise AssertionError("网络错误不应改用作品链接解析")

    monkeypatch.setattr(douyin_handler.MixIdFetcher, "get_mix_id", get_mix_id)
    monkeypatch.setattr(douyin_handler.AwemeIdFetcher, "get_aweme_id", get_aweme_id)

    with pytest.raises(APIConnectionError):
        await make_handler().handle_user_mix()
