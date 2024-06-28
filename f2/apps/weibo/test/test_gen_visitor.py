import pytest
from f2.apps.weibo.utils import VisitorManager


@pytest.mark.asyncio
async def test_gen_visitor():
    # 设置测试用的 visitor_conf
    VisitorManager.visitor_conf = {
        "cb": "visitor_gray_callback",
        "tid": "",
        "from": "weibo",
        "url": "https://passport.weibo.com/visitor/genvisitor2",
    }

    # 设置假的 proxies 和 user agent
    VisitorManager.proxies = {
        "http://": None,
        "https://": None,
    }

    visitor_cookie = await VisitorManager.gen_visitor()

    # 断言生成的 cookie 是否正确
    assert "SUB=" in visitor_cookie
    assert "SUBP=" in visitor_cookie
    assert "SRT=" in visitor_cookie
    assert "SRF=" in visitor_cookie
