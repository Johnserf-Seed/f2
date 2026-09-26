# path: tests/test_tiktok_device_cookie.py

import httpx

from f2.apps.tiktok.utils import DeviceIdManager
from f2.utils.http.cookie import parse_cookie_str

PAGE = (
    '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
    '{"__DEFAULT_SCOPE__": {"webapp.app-context": {"wid": "7360000000000000001"}}}'
    "</script>"
)
SET_COOKIES = [
    # 值里带逗号：多个头拼成一行后按逗号切分会被截断成 "abc"
    "tt_chain_token=abc, Def==; expires=Fri, 25-Sep-2027 12:00:00 GMT; path=/",
    "ttwid=1%7Cxyz; path=/; domain=.tiktok.com",
]


async def test_gen_device_id_collects_every_set_cookie(monkeypatch):
    def handler(request):
        return httpx.Response(
            200, text=PAGE, headers=[("set-cookie", c) for c in SET_COOKIES]
        )

    def init(self):
        self._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(DeviceIdManager, "__init__", init)
    # 请求头里的 msToken 会联网获取，测试中换成固定值
    monkeypatch.setattr(
        DeviceIdManager,
        "_device_id_headers",
        classmethod(lambda cls: {"User-Agent": "f2-test"}),
    )

    result = await DeviceIdManager.gen_device_id()

    assert result["deviceId"] == "7360000000000000001"
    assert parse_cookie_str(result["cookie"]) == {
        "tt_chain_token": "abc, Def==",
        "ttwid": "1%7Cxyz",
    }
