# path: f2/exceptions/file_exceptions.py

from f2.log.logger import logger
from f2.i18n.translator import _


class FileError(Exception):
    """基本的文件错误异常类，其他文件异常都会继承这个类"""

    def __init__(self, message, filepath=None):
        logger.error(_("请前往QA文档 https://f2.wiki/faq 查看相关帮助"))
        self.filepath = filepath
        super().__init__(message)

    def __str__(self):
        """返回错误信息和文件路径（如果有的话）"""
        return f"{super().__str__()} Filepath: {self.filepath}" if self.filepath else ""


class FileNotFound(FileError):
    """文件不存在错误"""

    def __init__(self, message=None, filepath=None):
        super().__init__(message, filepath)


class FilePermissionError(FileError):
    """文件权限错误"""

    def __init__(self, message, filepath=None):
        super().__init__(message, filepath)


class FileReadError(FileError):
    """文件读取错误"""

    def __init__(self, message, filepath=None):
        super().__init__(message, filepath)


class FileWriteError(FileError):
    """文件写入错误"""

    def __init__(self, message, filepath=None):
        super().__init__(message, filepath)
