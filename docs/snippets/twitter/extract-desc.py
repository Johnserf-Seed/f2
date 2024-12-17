from f2.apps.twitter.utils import extract_desc
from f2.log.logger import logger


def main():
    raw_desc = {
        "xxx https://t.co/SfB6v3Kx1z",
        "https://t.co/SfB6v3Kx1z",
        "   ",
    }

    for text_raw in raw_desc:
        desc = extract_desc(text_raw)
        logger.info(f"提取结果: {desc}")


if __name__ == "__main__":
    main()
