# path: tests/test_xbogus.py

from f2.utils.xbogus import XBogus

xb = XBogus().getXBogus(
    "aweme_id=7196239141472980280&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333"
)
print(xb)
