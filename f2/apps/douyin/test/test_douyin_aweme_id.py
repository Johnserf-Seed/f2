import asyncio
from f2.apps.douyin.utils import AwemeIdFetcher


async def main():
    test_urls = [
        "0.53 02/26 I@v.sE Fus:/ 你别太帅了郑润泽# 现场版live # 音乐节 # 郑润泽  https://v.douyin.com/iRNBho6u/ 复制此链接，打开Dou音搜索，直接观看视频!",
        "https://v.douyin.com/iRNBho6u/",
        "https://v.douyin.com/iNUBcHxM/",
        "https://www.iesdouyin.com/share/video/7298145681699622182/?region=CN&mid=7298145762238565171&u_code=l1j9bkbd&did=MS4wLjABAAAAtqpCx0hpOERbdSzQdjRZw-wFPxaqdbAzsKDmbJMUI3KWlMGQHC-n6dXAqa-dM2EP&iid=MS4wLjABAAAANwkJuWIRFOzg5uCpDRpMj4OX-QryoDgn-yYlXQnRwQQ&with_sec_did=1&titleType=title&share_sign=05kGlqGmR4_IwCX.ZGk6xuL0osNA..5ur7b0jbOx6cc-&share_version=170400&ts=1699262937&from_aid=6383&from_ssr=1&from=web_code_link",
        "https://www.douyin.com/video/7298145681699622182?previous_page=web_code_link",
        "https://www.douyin.com/video/7298145681699622182",
        "https://www.douyin.com/note/7330042216045464883",
    ]

    for url in test_urls:
        print(await AwemeIdFetcher.get_aweme_id(url))

    aweme_id = await AwemeIdFetcher.get_all_aweme_id(test_urls)
    print(aweme_id)


if __name__ == "__main__":
    asyncio.run(main())
