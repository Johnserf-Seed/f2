from f2.apps.weibo.utils import extract_desc
from f2.log.logger import logger


def main():
    raw_desc = {
        "超大颗花生汤圆[舔屏] http://t.cn/A6nqzsFe",
        "分享视频 http://t.cn/A6nNyQyS ​​​",
        "香宝宝   http://t.cn/A6mwArY7 ​​​",
        "  总有人类想要变成小猫咪^⌯𖥦⌯^ ੭   http://t.cn/A6n1zhGt ​​​",
        "过来挨踢[亲亲]      http://t.cn/A6ndh6PS ​​​",
        "单独的文案   ",  # 没有链接的情况
        "http://t.cn/A6nqzsFe",  # 只有链接的情况
        "   ",  # 空字符串或空白内容
    }

    for text_raw in raw_desc:
        desc = extract_desc(text_raw)
        logger.info(f"提取结果: {desc}")


if __name__ == "__main__":
    main()
