# path: f2/exceptions/api_exceptions.py
from f2.log.logger import logger


class APIError(Exception):
    """基本API异常类，其他API异常都会继承这个类"""

    def __init__(self, message=None, status_code=None):
        logger.error(
            "请前往QA文档 https://johnserf-seed.github.io/f2/question-answer/qa.html 查看相关帮助"
        )
        self.status_code = status_code
        super().__init__(message)

    def __str__(self):
        """返回错误信息和文件路径（如果有的话）"""
        return f"{super().__str__()}" + (
            f" Status Code: {self.status_code}" if self.status_code else ""
        )


class APIConnectionError(APIError):
    """当与API的连接出现问题时抛出"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)


class APIUnavailableError(APIError):
    """当API服务不可用时抛出，例如维护或超时"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)


class APINotFoundError(APIError):
    """当API端点不存在时抛出"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)


class APIResponseError(APIError):
    """当API返回的响应与预期不符时抛出"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)


class APIRateLimitError(APIError):
    """当达到API的请求速率限制时抛出"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)


class APITimeoutError(APIError):
    """当API请求超时时抛出"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)


class APIUnauthorizedError(APIError):
    """当API请求由于授权失败而被拒绝时抛出"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)


class APIRetryExhaustedError(APIError):
    """当API请求重试次数用尽时抛出"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message, status_code)
