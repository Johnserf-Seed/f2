# path: f2/exceptions/conf_exceptions.py

from f2.log.logger import logger
from f2.i18n.translator import _


class ConfError(Exception):
    """基本配置异常类，其他配置异常都会继承这个类"""

    def __init__(self, message=None, filepath=None, key=None, value=None):
        self.filepath = filepath
        self.key = key
        self.value = value

        # 记录日志，包含更多详细信息
        log_message = _("配置错误: {message}").format(message=message or _("未知错误"))
        if filepath:
            log_message += f" | Filepath: {filepath}"
        if key:
            log_message += f" | Key: {key}"
        if value:
            log_message += f" | Value: {value}"

        logger.error(log_message)
        logger.error(_("请前往 QA 文档 https://f2.wiki/faq 查看相关帮助"))

        super().__init__(message)

    def __str__(self):
        """返回详细的错误信息"""
        parts = [super().__str__()]
        if self.filepath:
            parts.append(f"Filepath: {self.filepath}")
        if self.key:
            parts.append(f"Key: {self.key}")
        if self.value:
            parts.append(f"Value: {self.value}")
        return " | ".join(parts)


class InvalidEncodingError(ConfError):
    """提示用户配置包含非ASCII字符"""

    def __init__(self, key=None, value=None):
        message = _("请确保所有配置项和值均为 ASCII 或 UTF-8 编码的字符串")
        if key and value:
            message += f" | Key: {key}, Value: {value}"
        super().__init__(message=message, key=key, value=value)


class InvalidConfError(ConfError):
    """提示用户配置文件格式错误"""

    def __init__(self, key=None, value=None):
        if value is None or value == "":
            message = _(
                "请检查配置文件格式是否正确: {key} 不能为空，使用默认配置"
            ).format(key=key)
        else:
            message = _(
                "请检查配置文件格式是否正确 | Key: {key}, Value: {value}，使用默认配置"
            ).format(key=key, value=value)
        super().__init__(message=message, key=key, value=value)


class InvalidConfPathError(ConfError):
    """提示用户配置文件路径错误"""

    def __init__(self, filepath=None):
        message = _("请检查配置文件路径是否正确")
        if filepath:
            message += f" | Filepath: {filepath}"
        super().__init__(message=message, filepath=filepath)
