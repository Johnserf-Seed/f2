import pytest
from f2.apps.douyin.model import UserPost
from f2.apps.douyin.utils import XBogusManager
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint


def test_xbogus_manager():
    params = UserPost(
        max_cursor=0,
        count=20,
        sec_user_id="MS4wLjABAAAA5OCaznf4ihGfC65u0imbLzmBOuWDpUMo58CdnVTcX_R8bD9HZQknOJ4ZX9FdZnIq",
    )

    final_endpoint = XBogusManager.to_complete_endpoint(
        dyendpoint.USER_DETAIL, params.dict()
    )

    assert final_endpoint, "Failed to get a final endpoint."
