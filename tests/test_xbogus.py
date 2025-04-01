# path: tests/test_xbogus.py

from f2.utils.crypto.bytedance.xbogus import XBogus


def test_get_xbogus():
    xb = XBogus().getXBogus(
        "aweme_id=7196239141472980280&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333"
    )
    assert xb is not None
