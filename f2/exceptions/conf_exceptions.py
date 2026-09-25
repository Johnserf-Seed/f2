# path: f2/exceptions/conf_exceptions.py

from f2.exceptions.base import F2Error
from f2.i18n.translator import _


class ConfError(F2Error):
    """
    基本配置异常类，其他配置异常都会继承这个类

    文件路径、配置键与值会拼接在 `str()` 结果中；异常在构造时不记录日志。
    """

    def __init__(self, message=None, filepath=None, key=None, value=None):
        self.filepath = filepath
        self.key = key
        self.value = value
        super().__init__(message)

    def __str__(self):
        """返回详细的错误信息，子类已写进消息的字段不再重复追加"""
        message = super().__str__()
        parts = [message]
        for label, detail in (
            ("Filepath", self.filepath),
            ("Key", self.key),
            ("Value", self.value),
        ):
            if detail and str(detail) not in message:
                parts.append(f"{label}: {detail}")
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
