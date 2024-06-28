// #region single-aweme-id-snippet
import asyncio
from f2.apps.douyin.utils import AwemeIdFetcher


async def main():
    raw_url = (
        "https://www.douyin.com/video/7298145681699622182?previous_page=web_code_link"
    )
    return await AwemeIdFetcher.get_aweme_id(raw_url)


if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion single-aweme-id-snippet


// #region multi-aweme-id-snippet
import asyncio
from f2.apps.douyin.utils import AwemeIdFetcher
from f2.utils.utils import extract_valid_urls


async def main():
    raw_urls = [
        "0.53 02/26 I@v.sE Fus:/ 你别太帅了郑润泽# 现场版live # 音乐节 # 郑润泽  https://v.douyin.com/iRNBho6u/ 复制此链接，打开Dou音搜索，直接观看视频!",
        "https://v.douyin.com/iRNBho6u/",
        "https://www.iesdouyin.com/share/video/7298145681699622182/?region=CN&mid=7298145762238565171&u_code=l1j9bkbd&did=MS4wLjABAAAAtqpCx0hpOERbdSzQdjRZw-wFPxaqdbAzsKDmbJMUI3KWlMGQHC-n6dXAqa-dM2EP&iid=MS4wLjABAAAANwkJuWIRFOzg5uCpDRpMj4OX-QryoDgn-yYlXQnRwQQ&with_sec_did=1&titleType=title&share_sign=05kGlqGmR4_IwCX.ZGk6xuL0osNA..5ur7b0jbOx6cc-&share_version=170400&ts=1699262937&from_aid=6383&from_ssr=1&from=web_code_link",
        "https://www.douyin.com/video/7298145681699622182?previous_page=web_code_link",
        "https://www.douyin.com/video/7298145681699622182",
    ]

    # 提取有效URL
    urls = extract_valid_urls(raw_urls)

    # 对于URL列表
    return await AwemeIdFetcher.get_all_aweme_id(urls)


if __name__ == "__main__":
    print(asyncio.run(main()))

// #endregion multi-aweme-id-snippet