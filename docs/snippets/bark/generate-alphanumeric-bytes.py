from f2.apps.bark.utils import generate_alphanumeric_bytes
from f2.log.logger import logger

if __name__ == "__main__":
    length = 16
    logger.info(
        f"生成的字节长度为 {length} 的字母数字字节: {generate_alphanumeric_bytes(length)}"
    )
