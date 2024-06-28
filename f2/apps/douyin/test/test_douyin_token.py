import pytest
from f2.apps.douyin.utils import TokenManager


def test_gen_real_msToken():
    token = TokenManager.gen_real_msToken()
    assert token is not None, "gen_real_msToken() should return a valid token"
    assert isinstance(token, str), "gen_real_msToken() should return a string"


def test_gen_false_msToken():
    token = TokenManager.gen_false_msToken()
    assert token is not None, "gen_false_msToken() should return a valid token"
    assert isinstance(token, str), "gen_false_msToken() should return a string"


def test_gen_ttwid():
    ttwid = TokenManager.gen_ttwid()
    assert ttwid is not None, "gen_ttwid() should return a valid ttwid"
    assert isinstance(ttwid, str), "gen_ttwid() should return a string"


def test_gen_webid():
    webid = TokenManager.gen_webid()
    assert webid is not None, "gen_webid() should return a valid webid"
    assert isinstance(webid, str), "gen_webid() should return a string"
