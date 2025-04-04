# region single-webcast-id-snippet
import asyncio

from f2.apps.douyin.utils import WebCastIdFetcher


async def main():
    raw_url = "https://live.douyin.com/775841227732"
    return await WebCastIdFetcher.get_webcast_id(raw_url)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion single-webcast-id-snippet


# region multi-webcast-id-snippet
import asyncio

from f2.apps.douyin.utils import WebCastIdFetcher
from f2.utils.string.formatter import extract_valid_urls


async def main():
    raw_urls = [
        "https://live.douyin.com/775841227732",
        "https://live.douyin.com/775841227732?room_id=7318296342189919011&enter_from_merge=web_share_link&enter_method=web_share_link&previous_page=app_code_link",
        'https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011?u_code=l1j9bkbd&did=MS4wLjABAAAAEs86TBQPNwAo-RGrcxWyCdwKhI66AK3Pqf3ieo6HaxI&iid=MS4wLjABAAAA0ptpM-zzoliLEeyvWOCUt-_dQza4uSjlIvbtIazXnCY&with_sec_did=1&use_link_command=1&ecom_share_track_params=&extra_params={"from_request_id":"20231230162057EC005772A8EAA0199906","im_channel_invite_id":"0"}&user_id=3644207898042206&liveId=7318296342189919011&from=share&style=share&enter_method=click_share&roomId=7318296342189919011&activity_info={}',
        "6i- Q@x.Sl 03/23 【醒子8ke的直播间】  点击打开👉https://v.douyin.com/i8tBR7hX/  或长按复制此条消息，打开抖音，看TA直播",
        "https://v.douyin.com/i8tBR7hX/",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await WebCastIdFetcher.get_all_webcast_id(urls)


if __name__ == "__main__":
    print(asyncio.run(main()))

# endregion multi-webcast-id-snippet
