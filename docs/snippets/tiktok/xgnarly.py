# region model-2-endpoint-snippet
# 使用用户作品模型生成带新版签名的请求链接
from f2.apps.tiktok.api import TiktokAPIEndpoints as tkendpoint
from f2.apps.tiktok.model import UserPost
from f2.apps.tiktok.utils import XGnarlyManager


def main():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    cookie = "YOUR_COOKIE"  # msToken 从 cookie 中读取，请求头中的 Cookie 也要用同一个值
    secUid = (
        "MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
    )
    params = UserPost(secUid=secUid)
    return XGnarlyManager.model_2_endpoint(
        user_agent, tkendpoint.USER_POST, params.model_dump(), cookie
    )


if __name__ == "__main__":
    print(main())

# endregion model-2-endpoint-snippet
