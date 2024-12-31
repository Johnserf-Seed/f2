# path: f2/exceptions/conf_exceptions.py

from f2.log.logger import logger
from f2.i18n.translator import _


class ConfError(Exception):
    """基本配置异常类，其他配置异常都会继承这个类"""

    def __init__(self, message=None):
        logger.error(_("请前往QA文档 https://f2.wiki/faq 查看相关帮助"))
        super().__init__(message)

    def __str__(self) -> str:
        return super().__str__()


class InvalidEncodingError(ConfError):
    """提示用户配置包含非ASCII字符。"""

    def __init__(self, message=None):
        # 动态生成消息，包含出错的 key 和 value
        if message is None:
            message = _("请确保所有配置项和值均为ASCII或UTF-8编码的字符串")

        logger.error(message)

        super().__init__(message=message)
