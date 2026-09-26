# path: tests/test_set_cookie.py

import httpx

from f2.utils.http.cookie import join_set_cookie_headers, parse_cookie_str


def headers(*set_cookies):
    return httpx.Response(200, headers=[("set-cookie", c) for c in set_cookies]).headers


def test_join_set_cookie_headers_keeps_every_cookie_and_full_values():
    joined = join_set_cookie_headers(
        headers(
            "SUB=_2AkMabc; expires=Fri, 25-Sep-2027 12:00:00 GMT; path=/; secure",
            # 值里带逗号：多个头拼成一行后按逗号切分会被截断
            "tid=abc, Def__095; path=/",
            "SUBP=0033WrSX; path=/",
        )
    )
    assert joined == "SUB=_2AkMabc; tid=abc, Def__095; SUBP=0033WrSX"
    assert parse_cookie_str(joined)["tid"] == "abc, Def__095"


def test_join_set_cookie_headers_without_set_cookie():
    assert join_set_cookie_headers(headers()) == ""
