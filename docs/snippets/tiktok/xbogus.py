// #region str-2-endpoint-snippet
# 使用接口地址直接生成请求链接
import asyncio
from f2.apps.tiktok.utils import XBogusManager

async def main():
    test_endpoint = "aid=1988&app_language=zh-Hans&app_name=tiktok_web&browser_platform=Win32&browser_version=5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F120.0.0.0%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&count=16&coverFormat=2&device_id=7306060721837852167&device_platform=web_pc&itemID=7294298719665622305"
    return XBogusManager.str_2_endpoint(test_endpoint)

if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion str-2-endpoint-snippet


// #region model-2-endpoint-snippet
# 使用用户信息模型生成请求链接
import asyncio
from f2.apps.tiktok.api import TiktokAPIEndpoints as tkendpoint
from f2.apps.tiktok.model import UserProfile
from f2.apps.tiktok.utils import XBogusManager

async def gen_user_profile(params: UserProfile):
    return XBogusManager.model_2_endpoint(
        tkendpoint.USER_DETAIL, params.model_dump()
    )

async def main():
    secUid="MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
    params = UserProfile(secUid=secUid)
    return await gen_user_profile(params)

if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion model-2-endpoint-snippet


// #region model-2-endpoint-2-filter-snippet
# 使用用户信息模型生成请求链接，请求接口并使用自定义过滤器输出所需接口数据
import asyncio
from f2.apps.tiktok.api import TiktokAPIEndpoints as tkendpoint
from f2.apps.tiktok.crawler import TiktokCrawler
from f2.apps.tiktok.model import UserProfile
from f2.apps.tiktok.filter import UserProfileFilter
from f2.apps.tiktok.utils import XBogusManager

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Referer": "https://www.tiktok.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    async with TiktokCrawler(kwargs) as crawler:
        secUid="MS4wLjABAAAAQhcYf_TjRKUku-aF8oqngAfzrYksgGLRz8CKMciBFdfR54HQu3qGs-WoJ-KO7hO8"
        params = UserProfile(secUid=secUid)
        response = await crawler.fetch_user_profile(params)
        user = UserProfileFilter(response)
        # return user # user为UserProfileFilter对象，需要调用_to_dict()方法转为字典格式
        return user._to_dict()

if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion model-2-endpoint-2-filter-snippet