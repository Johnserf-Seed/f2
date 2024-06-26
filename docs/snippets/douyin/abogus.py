// #region str-2-endpoint-snippet
# 使用接口地址直接生成请求链接
import asyncio
from f2.apps.douyin.utils import ABogusManager, ClientConfManager


async def main():
    request = "GET"
    test_endpoint = "device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=7380308675841297704&update_version_code=170400&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=125.0.0.0&browser_online=true&engine_name=Blink&engine_version=125.0.0.0&os_name=Windows&os_version=10&cpu_core_num=12&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7376294349792396827"
    return ABogusManager.str_2_endpoint(
        ClientConfManager.user_agent(),
        endpoint=test_endpoint,
        request=request,
    )


if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion str-2-endpoint-snippet


// #region model-2-endpoint-snippet
# 使用用户信息模型生成请求链接
import asyncio
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint
from f2.apps.douyin.model import UserProfile
from f2.apps.douyin.utils import ABogusManager, ClientConfManager


async def gen_user_profile(params: UserProfile):
    return ABogusManager.model_2_endpoint(
        ClientConfManager.user_agent(),
        base_endpoint=dyendpoint.USER_DETAIL,
        params=params.model_dump(),
        request = "GET",
    )


async def main():
    sec_user_id="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
    params = UserProfile(sec_user_id=sec_user_id)
    return await gen_user_profile(params)


if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion model-2-endpoint-snippet


// #region model-2-endpoint-2-filter-snippet
# 使用用户信息模型生成请求链接，请求接口并使用自定义过滤器输出所需接口数据
import asyncio
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint
from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.model import UserProfile
from f2.apps.douyin.filter import UserProfileFilter


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    async with DouyinCrawler(kwargs) as crawler:
        sec_user_id="MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
        params = UserProfile(sec_user_id=sec_user_id)
        response = await crawler.fetch_user_profile(params)
        user = UserProfileFilter(response)
        # return user # user为UserProfileFilter对象，需要调用_to_dict()方法转为字典格式
        return user._to_dict()

if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion model-2-endpoint-2-filter-snippet