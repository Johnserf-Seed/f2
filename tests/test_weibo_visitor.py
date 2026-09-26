# path: tests/test_weibo_visitor.py

import httpx

from f2.apps.weibo.utils import VisitorManager
from f2.utils.http.cookie import parse_cookie_str

SET_COOKIES = [
    "SUB=_2AkMabc; expires=Fri, 25-Sep-2027 12:00:00 GMT; path=/; "
    "domain=.weibo.com; secure; httponly",
    "SUBP=0033WrSX; expires=Fri, 25-Sep-2027 12:00:00 GMT; path=/; domain=.weibo.com",
    # 值里带逗号：多个头拼成一行后按逗号切分会被截断成 "abc"
    "tid=abc, Def__095; path=/",
]


async def test_gen_visitor_collects_every_set_cookie(monkeypatch):
    def handler(request):
        return httpx.Response(200, headers=[("set-cookie", c) for c in SET_COOKIES])

    def init(self):
        self._aclient = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(VisitorManager, "__init__", init)

    cookie = parse_cookie_str(await VisitorManager.gen_visitor())
    assert cookie == {"SUB": "_2AkMabc", "SUBP": "0033WrSX", "tid": "abc, Def__095"}
