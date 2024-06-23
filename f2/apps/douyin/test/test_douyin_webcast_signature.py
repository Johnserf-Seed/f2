import pytest
from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature
from f2.apps.douyin.utils import ClientConfManager


def test_DouyinWebcastSignature():
    room_id = "7383573503129258802"
    user_unique_id = "7383588170770138661"
    signature = DouyinWebcastSignature(ClientConfManager.user_agent()).get_signature(
        room_id, user_unique_id
    )
    assert signature is not None
    assert len(signature) == 16
