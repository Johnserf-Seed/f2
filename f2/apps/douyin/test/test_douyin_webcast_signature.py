from f2.apps.douyin.algorithm.webcast_signature import DouyinWebcastSignature


def test_DouyinWebcastSignature():
    room_id = "7383573503129258802"
    user_unique_id = "7383588170770138661"
    signature = DouyinWebcastSignature().get_signature(room_id, user_unique_id)
    assert signature is not None
    assert len(signature) == 16
