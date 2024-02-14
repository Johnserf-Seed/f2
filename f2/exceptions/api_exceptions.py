# path: f2/exceptions/api_exceptions.py

from f2.cli.cli_console import RichConsoleManager

exception_console = RichConsoleManager().exception_console


class APIError(Exception):
    """基本API异常类，其他API异常都会继承这个类"""

    def __init__(self, status_code=None):
        self.status_code = status_code
        exception_console.print(
            "请前往QA文档 https://johnserf-seed.github.io/f2/question-answer/qa.html 查看相关帮助"
        )

    def display_error(self):
        """显示错误信息和状态码（如果有的话）"""
        return f"Error: {self.args[0]}." + (
            f" Status Code: {self.status_code}." if self.status_code else ""
        )


class APIConnectionError(APIError):
    """当与API的连接出现问题时抛出"""

    def display_error(self):
        return f"API Connection Error: {self.args[0]}."


class APIUnavailableError(APIError):
    """当API服务不可用时抛出，例如维护或超时"""

    def display_error(self):
        return f"API Unavailable Error: {self.args[0]}."


class APINotFoundError(APIError):
    """当API端点不存在时抛出"""

    def display_error(self):
        return f"API Not Found Error: {self.args[0]}."


class APIResponseError(APIError):
    """当API返回的响应与预期不符时抛出"""

    def display_error(self):
        return f"API Response Error: {self.args[0]}."


class APIRateLimitError(APIError):
    """当达到API的请求速率限制时抛出"""

    def display_error(self):
        return f"API Rate Limit Error: {self.args[0]}."


class APITimeoutError(APIError):
    """当API请求超时时抛出"""

    def display_error(self):
        return f"API Timeout Error: {self.args[0]}."


class APIUnauthorizedError(APIError):
    """当API请求由于授权失败而被拒绝时抛出"""

    def display_error(self):
        return f"API Unauthorized Error: {self.args[0]}."


class APIRetryExhaustedError(APIError):
    """当API请求重试次数用尽时抛出"""

    def display_error(self):
        return f"API Retry Exhausted Error: {self.args[0]}."
