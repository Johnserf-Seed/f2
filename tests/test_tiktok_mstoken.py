# path: tests/test_tiktok_mstoken.py

import httpx
import pytest

from f2.apps.tiktok.utils import TokenManager
from f2.exceptions.api_exceptions import APIResponseError


def mock_mssdk(monkeypatch, **response_kwargs):
    def handler(request):
        return httpx.Response(200, json={}, **response_kwargs)

    monkeypatch.setattr(
        TokenManager,
        "_create_mount",
        lambda self, async_mode=False: {"all://": httpx.MockTransport(handler)},
    )


def test_gen_real_mstoken_accepts_the_current_length(monkeypatch):
    # 2026-09 起 mssdk 下发的 msToken 为 168 位，此前为 152 位
    token = "A" * 167 + "="
    mock_mssdk(monkeypatch, headers={"set-cookie": f"msToken={token}; Path=/"})
    assert TokenManager.gen_real_msToken() == token


def test_gen_real_mstoken_requires_the_cookie(monkeypatch):
    mock_mssdk(monkeypatch)
    with pytest.raises(APIResponseError):
        TokenManager.gen_real_msToken()
