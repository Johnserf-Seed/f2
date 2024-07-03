# path: f2/apps/douyin/algorithm/webcast_signature.py

import execjs
import hashlib
from pathlib import Path
from f2.utils.utils import get_resource_path


class DouyinWebcastSignature:
    def __init__(self, user_agent: str = None):
        self.user_agent = (
            user_agent
            if user_agent is not None and user_agent != ""
            else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        )  # 自定义 ua，为空则设置一个默认 ua

    def get_signature(self, room_id: str, user_unique_id: str) -> str:
        """
        获取直播间签名

        Args:
            room_id: (str) 直播间 ID
            user_unique_id: (str) 用户唯一 ID

        Returns:
            signature: (str) 签名
        """
        # 使用 importlib_resources 读取库中的 js 文件
        js_path = get_resource_path("apps/douyin/algorithm/webcast_signature.js")
        # 读取 js 文件，确保使用 utf-8 编码
        js_code = Path(js_path).read_text()

        # 在 js_code 中动态设置 user_agent
        js_code = f"""
        _navigator = {{
            userAgent: "{self.user_agent}"
        }};
        {js_code}
        """

        # 创建 execjs 运行环境
        ctx = execjs.compile(js_code)

        # 构造待 signature 的字符串
        raw_string = f"live_id=1,aid=6383,version_code=180800,webcast_sdk_version=1.0.14-beta.0,room_id={room_id},sub_room_id=,sub_channel_id=,did_rule=3,user_unique_id={user_unique_id},device_platform=web,device_type=,ac=,identity=audience"

        # md5 计算 X-MS-STUB
        x_ms_stub = {"X-MS-STUB": hashlib.md5(raw_string.encode("utf-8")).hexdigest()}

        # 调用 js 函数计算 signature
        result = ctx.call("get_signature", x_ms_stub)

        # 加密参数的 key 为 X-Bogus
        return result.get("X-Bogus")


if __name__ == "__main__":
    signature_handler = DouyinWebcastSignature(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    )
    signature = signature_handler.get_signature(
        "7382517534467115826", "7382524529011246630"
    )
    print(signature)
