import asyncio

from f2.apps.weibo.handler import WeiboHandler
from f2.apps.weibo.utils import format_file_name


async def main():
    # 文件名模板
    kwargs = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Referer": "https://www.weibo.com/",
        },
        "naming": "{create}_{desc}_{weibo_id}",
        "cookie": "YOUR_COOKIE_HERE",
    }
    # 单作品的数据
    weibo_data = await WeiboHandler(kwargs).fetch_one_weibo(weibo_id="LvFY288c0")
    # 格式化后的文件名
    print(format_file_name(kwargs.get("naming"), weibo_data._to_dict()) + "_weibo")

    # 文件名模板
    kwargs = {
        # ...
        "naming": "{create}_{desc}_{weibo_id}_{location}",
        # ...
    }
    # 用户自定义字段
    custom_fields = {"location": "Guang dong"}
    # 格式化后的自定义文件名
    print(
        format_file_name(kwargs.get("naming"), weibo_data._to_dict(), custom_fields)
        + "_weibo"
    )


if __name__ == "__main__":
    asyncio.run(main())
