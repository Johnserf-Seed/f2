import asyncio

from f2.apps.douyin.handler import DouyinHandler
from f2.apps.douyin.utils import TokenManager

kwargs = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Referer": "https://www.douyin.com/",
    },
    "proxies": {"http://": None, "https://": None},
    "timeout": 10,
    "cookie": f"ttwid={TokenManager.gen_ttwid()}",
}


async def main():
    keyword = "不吃香菜"
    suggest_words = await DouyinHandler(kwargs).fetch_suggest_word(keyword)
    print("=================_to_raw================")
    print(suggest_words._to_raw())
    # print("=================_to_dict===============")
    # print(suggest_words._to_dict())
    # print("=================_to_list===============")
    # print(suggest_words._to_list())


if __name__ == "__main__":
    asyncio.run(main())
