# path: f2/exceptions/db_exceptions.py
from f2.log.logger import logger


class DatabaseError(Exception):
    """基本数据库异常类，其他数据库异常都会继承这个类"""

    def __init__(self, message=None, db=None):
        logger.error(
            "请前往QA文档 https://johnserf-seed.github.io/f2/question-answer/qa.html 查看相关帮助"
        )
        self.db = db
        super().__init__(message)

    def __str__(self):
        """返回错误信息和db（如果有的话）"""
        return f"{super().__str__()}" + (f" Database: {self.db}" if self.db else "")


class DatabaseConnectionError(DatabaseError):
    """当与数据库的连接出现问题时抛出"""

    def __init__(self, message=None, db=None):
        super().__init__(message, db)


class RecordNotFoundError(DatabaseError):
    """当在数据库中找不到预期的记录时抛出"""

    def __init__(self, message=None, db=None):
        super().__init__(message, db)


class MultipleRecordsFoundError(DatabaseError):
    """当期望找到一个记录但实际找到多个时抛出"""

    def __init__(self, message=None, db=None):
        super().__init__(message, db)


class DatabaseTimeoutError(DatabaseError):
    """当数据库操作超时时抛出"""

    def __init__(self, message=None, db=None):
        super().__init__(message, db)


class DatabaseConstraintError(DatabaseError):
    """当违反数据库约束时抛出，例如唯一性约束"""

    def __init__(self, message=None, db=None):
        super().__init__(message, db)
