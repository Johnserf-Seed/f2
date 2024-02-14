# path: f2/exceptions/db_exceptions.py

from f2.cli.cli_console import RichConsoleManager

exception_console = RichConsoleManager().exception_console


class DatabaseError(Exception):
    """基本数据库异常类，其他数据库异常都会继承这个类"""

    def __init__(self):
        exception_console.print(
            "请前往QA文档 https://johnserf-seed.github.io/f2/question-answer/qa.html 查看相关帮助"
        )

    def display_error(self):
        """显示错误信息"""
        return f"Database Error: {self.args[0]}."


class DatabaseConnectionError(DatabaseError):
    """当与数据库的连接出现问题时抛出"""

    def display_error(self):
        return f"Database Connection Error: {self.args[0]}."


class RecordNotFoundError(DatabaseError):
    """当在数据库中找不到预期的记录时抛出"""

    def display_error(self):
        return f"Record Not Found Error: {self.args[0]}."


class MultipleRecordsFoundError(DatabaseError):
    """当期望找到一个记录但实际找到多个时抛出"""

    def display_error(self):
        return f"Multiple Records Found Error: {self.args[0]}."


class DatabaseTimeoutError(DatabaseError):
    """当数据库操作超时时抛出"""

    def display_error(self):
        return f"Database Timeout Error: {self.args[0]}."


class DatabaseConstraintError(DatabaseError):
    """当违反数据库约束时抛出，例如唯一性约束"""

    def display_error(self):
        return f"Database Constraint Error: {self.args[0]}."
