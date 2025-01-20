# region str-2-endpoint-snippet
# 使用接口地址直接生成请求链接
from f2.apps.douyin.utils import XBogusManager, ClientConfManager


def main():
    test_endpoint = "aweme_id=7196239141472980280&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333"
    return XBogusManager.str_2_endpoint(
        ClientConfManager.user_agent(),
        endpoint=test_endpoint,
    )


if __name__ == "__main__":
    print(main())

# endregion str-2-endpoint-snippet


# region model-2-endpoint-snippet
# 使用用户信息模型生成请求链接
import asyncio
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint
from f2.apps.douyin.model import UserProfile
from f2.apps.douyin.utils import XBogusManager, ClientConfManager


async def gen_user_profile(params: UserProfile):
    return XBogusManager.model_2_endpoint(
        ClientConfManager.user_agent(),
        base_endpoint=dyendpoint.USER_DETAIL,
        params=params.model_dump(),
    )


async def main():
    sec_user_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
    params = UserProfile(sec_user_id=sec_user_id)
    return await gen_user_profile(params)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion model-2-endpoint-snippet


# region model-2-endpoint-2-filter-snippet
# 使用用户信息模型生成请求链接，请求接口并使用自定义过滤器输出所需接口数据
import asyncio
from f2.apps.douyin.api import DouyinAPIEndpoints as dyendpoint
from f2.apps.douyin.crawler import DouyinCrawler
from f2.apps.douyin.model import UserProfile
from f2.apps.douyin.filter import UserProfileFilter
from f2.apps.douyin.utils import XBogusManager, ClientConfManager


kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "cookie": "YOUR_COOKIE_HERE",
}


async def main():
    async with DouyinCrawler(kwargs) as crawler:
        sec_user_id = "MS4wLjABAAAANXSltcLCzDGmdNFI2Q_QixVTr67NiYzjKOIP5s03CAE"
        params = UserProfile(sec_user_id=sec_user_id)
        response = await crawler.fetch_user_profile(params)
        user = UserProfileFilter(response)
        # return user # user为UserProfileFilter对象，需要调用_to_dict()方法转为字典格式
        return user._to_dict()


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion model-2-endpoint-2-filter-snippet
