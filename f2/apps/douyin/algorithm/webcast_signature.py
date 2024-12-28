# path: f2/apps/douyin/algorithm/webcast_signature.py

import execjs
import hashlib
from pathlib import Path
from f2.utils.utils import get_resource_path


class DouyinWebcastSignature:
    """
    抖音直播间签名生成器 (Douyin Webcast Signature Generator)

    该类用于生成抖音直播间的签名，通过传入直播间 ID 和用户唯一 ID，计算并返回签名。签名通过执行 JavaScript 代码计算生成，并结合其他参数进行 MD5 加密。

    类属性:
    - user_agent (str): 自定义的用户代理字符串。如果未指定，使用默认的浏览器 UA。

    类方法:
    - __init__: 初始化方法，接受一个可选的 user_agent 参数，用于设置请求头中的用户代理。
    - get_signature: 根据直播间 ID 和用户唯一 ID 生成签名。

    异常处理:
    - 在获取签名过程中，可能会由于 JavaScript 执行错误或文件读取问题而抛出异常。

    使用示例:
    ```python
        # 创建 DouyinWebcastSignature 实例
        signature_handler = DouyinWebcastSignature(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0")

        # 获取直播间签名
        signature = signature_handler.get_signature("7382517534467115826", "7382524529011246630")

        # 输出签名
        print(signature)
    ```

    备注:
    - 该类利用 `execjs` 执行 JavaScript 代码来计算签名，需要确保 `webcast_signature.js` 文件存在，并且 JavaScript 函数能够正常执行。
    - 使用 `hashlib` 对原始字符串进行 MD5 加密，计算出的 `X-MS-STUB` 是签名的一部分。
    - `get_signature` 方法返回一个字典形式的结果，其中 `X-Bogus` 为最终签名。

    依赖:
    - `execjs` 用于执行 JavaScript 代码。
    - `hashlib` 用于计算 MD5 值。
    """

    def __init__(self, user_agent: str = None):
        self.user_agent = (
            user_agent
            if user_agent is not None and user_agent != ""
            else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
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
        x_ms_stub = hashlib.md5(raw_string.encode("utf-8")).hexdigest()

        # 调用 js 函数计算 signature
        result = ctx.call("get_signature", x_ms_stub)

        # 加密参数的 key 为 X-Bogus
        return result.get("X-Bogus")


if __name__ == "__main__":
    signature_handler = DouyinWebcastSignature(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    )
    signature = signature_handler.get_signature(
        "7382517534467115826", "7382524529011246630"
    )
    print(signature)
