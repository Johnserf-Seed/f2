from f2.apps.bark.utils import generate_numeric_bytes
from f2.log.logger import logger

if __name__ == "__main__":
    length = 10
    logger.info(
        f"生成的字节长度为 {length} 的纯数字字节: {generate_numeric_bytes(length)}"
    )
