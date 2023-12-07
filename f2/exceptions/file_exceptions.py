# path: f2/exceptions/file_exceptions.py

from f2.cli.cli_console import RichConsoleManager

exception_console = RichConsoleManager().exception_console


class FileError(Exception):
    """基本的文件错误异常类，其他文件异常都会继承这个类"""

    def __init__(self, message, filepath=None):
        super().__init__(message)
        self.filepath = filepath

    def display_error(self):
        """显示错误信息和文件路径（如果有的话）"""
        message = f"File Error: {self.args[0]}." + (
            f" Filepath: {self.filepath}." if self.filepath else ""
        )
        exception_console.print(message)
        return message


class FileNotFound(FileError, FileNotFoundError):
    """文件不存在错误"""

    def display_error(self):
        message = f"File Not Found Error: {self.args[0]}." + (
            f" Filepath: {self.filepath}." if self.filepath else ""
        )
        exception_console.print(message)
        return message


class FilePermissionError(FileError, PermissionError):
    """文件权限错误"""

    def display_error(self):
        message = f"File Permission Error: {self.args[0]}." + (
            f" Filepath: {self.filepath}." if self.filepath else ""
        )
        exception_console.print(message)
        return message


class FileReadError(FileError):
    """文件读取错误"""

    def display_error(self):
        message = f"File Read Error: {self.args[0]}." + (
            f" Filepath: {self.filepath}." if self.filepath else ""
        )
        exception_console.print(message)
        return message


class FileWriteError(FileError):
    """文件写入错误"""

    def display_error(self):
        message = f"File Write Error: {self.args[0]}." + (
            f" Filepath: {self.filepath}." if self.filepath else ""
        )
        exception_console.print(message)
        return message
