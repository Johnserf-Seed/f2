import pytest
from f2.apps.douyin.model import UserPost
from f2.apps.douyin.utils import XBogusManager, ABogusManager
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint


def test_xbogus_manager():
    params = UserPost(
        max_cursor=0,
        count=20,
        sec_user_id="MS4wLjABAAAA5OCaznf4ihGfC65u0imbLzmBOuWDpUMo58CdnVTcX_R8bD9HZQknOJ4ZX9FdZnIq",
    )

    final_endpoint = XBogusManager.model_2_endpoint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        base_endpoint=dyendpoint.USER_DETAIL,
        params=params.model_dump(),
    )

    assert final_endpoint, "Failed to get a final endpoint."


def test_abogus_manager():
    params = UserPost(
        max_cursor=0,
        count=20,
        sec_user_id="MS4wLjABAAAA5OCaznf4ihGfC65u0imbLzmBOuWDpUMo58CdnVTcX_R8bD9HZQknOJ4ZX9FdZnIq",
    )

    final_endpoint = ABogusManager.model_2_endpoint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        base_endpoint=dyendpoint.USER_DETAIL,
        params=params.model_dump(),
    )

    assert final_endpoint, "Failed to get a final endpoint."
