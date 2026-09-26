# path: tests/test_downloader_cookie.py

import pytest

from f2.apps.douyin.dl import DouyinDownloader
from f2.apps.douyin.handler import DouyinHandler
from f2.apps.tiktok.dl import TiktokDownloader
from f2.apps.twitter.dl import TwitterDownloader
from f2.apps.weibo.dl import WeiboDownloader
from f2.exceptions import ConfError, F2Error
from f2.log.redact import redact_text

BASE = {
    "headers": {"User-Agent": "f2-test"},
    "proxies": {"http://": None, "https://": None},
}
DOWNLOADERS = [DouyinDownloader, TiktokDownloader, TwitterDownloader, WeiboDownloader]


@pytest.mark.parametrize("downloader_cls", DOWNLOADERS)
@pytest.mark.parametrize("kwargs", [BASE, BASE | {"cookie": None}])
def test_missing_cookie_raises_conf_error(downloader_cls, kwargs):
    # 此前抛出 ValueError（没有 cookie 键时是 KeyError），CLI 会打印完整堆栈
    with pytest.raises(ConfError) as exc_info:
        downloader_cls(dict(kwargs))
    message = str(exc_info.value)
    assert exc_info.value.key == "cookie"
    assert "--auto-cookie" in message
    assert redact_text(message) == message


@pytest.mark.parametrize("downloader_cls", DOWNLOADERS)
async def test_empty_cookie_is_allowed(downloader_cls):
    # 抖音直播等请求不需要用户的 cookie，空字符串照常创建
    downloader = downloader_cls(BASE | {"cookie": ""})
    await downloader.close()


def test_handler_reports_missing_cookie_as_f2_error():
    with pytest.raises(F2Error):
        DouyinHandler(dict(BASE))
