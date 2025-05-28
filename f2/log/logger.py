# path: f2/log/logger.py

import datetime
import logging
import os
import time
import uuid
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler

from f2.utils.core.singleton import Singleton


class TrueLazyFileHandler(logging.Handler):
    """真正延迟创建文件的日志处理器"""

    def __init__(self, filename, when="h", interval=1, backupCount=0, encoding=None):
        super().__init__()
        self.filename = filename
        self.when = when
        self.interval = interval
        self.backupCount = backupCount
        self.encoding = encoding
        self._real_handler = None
        self._file_created = False

    def _create_real_handler(self):
        """创建真正的文件处理器"""
        if not self._file_created:
            # 确保目录存在
            Path(self.filename).parent.mkdir(parents=True, exist_ok=True)

            # 创建 TimedRotatingFileHandler
            self._real_handler = TimedRotatingFileHandler(
                self.filename,
                when=self.when,
                interval=self.interval,
                backupCount=self.backupCount,
                encoding=self.encoding,
            )

            # 复制格式器
            if self.formatter:
                self._real_handler.setFormatter(self.formatter)

            self._file_created = True

    def emit(self, record):
        """只有在真正需要记录日志时才创建文件"""
        if not self._file_created:
            self._create_real_handler()

        if self._real_handler:
            self._real_handler.emit(record)

    def close(self):
        """关闭处理器"""
        if self._real_handler:
            self._real_handler.close()
        super().close()

    def setFormatter(self, formatter):
        """设置格式器"""
        super().setFormatter(formatter)
        if self._real_handler:
            self._real_handler.setFormatter(formatter)


class LogManager(metaclass=Singleton):
    """
    日志管理器 (Log Manager)

    该类提供了一个全局日志管理器，使用单例模式，支持将日志输出到控制台和文件。

    文件日志会根据时间进行切割，每天生成一个新的日志文件，并保留一定数量的日志文件。

    还支持日志目录的管理和日志文件的清理功能。

    类属性:
    - logger (logging.Logger): 日志记录器实例，用于记录日志信息。
    - log_dir (Path | None): 日志文件存储路径。如果未设置，默认为 None。
    - _initialized (bool): 用于防止重复初始化。

    类方法:
    - __init__: 初始化日志管理器，并创建日志记录器实例。采用单例模式，确保只初始化一次。
    - setup_logging: 设置日志记录器的配置，包括日志级别、是否输出到控制台、日志文件路径等。
    - ensure_log_dir_exists: 确保日志目录存在。如果不存在，会自动创建。
    - clean_logs: 清理旧的日志文件，保留最新的n个日志文件。
    - shutdown: 关闭日志记录器并清理相关资源。

    异常处理:
    - 在清理日志文件时，如果日志文件正在被其他进程使用，将会捕获 `PermissionError` 异常，并记录警告信息。

    使用示例:
    ```python
        # 设置日志配置，并开始记录日志
        log_manager = LogManager()
        log_manager.setup_logging(log_to_console=True, log_path="./logs")

        # 清理过期日志，保留最新的10个日志文件
        log_manager.clean_logs(keep_last_n=10)

        # 使用日志记录器
        logger = logging.getLogger("f2")
        logger.info("This is an info message.")
    ```

    备注:
    - `setup_logging` 方法允许将日志输出到控制台和文件，并支持定期切割日志文件。
    - `clean_logs` 方法用于删除过期的日志文件，确保不会占用过多的磁盘空间。
    - 使用 `Singleton` 元类确保整个应用程序只有一个 `LogManager` 实例。
    """

    def __init__(self, log_name="f2"):
        if getattr(self, "_initialized", False):  # 防止重复初始化
            return

        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)
        self.log_dir = None
        self._initialized = True

    def setup_logging(
        self,
        level=logging.INFO,
        log_to_console=False,
        log_path=None,
        lazy_file_creation=False,
    ):
        self.logger.handlers.clear()
        self.logger.setLevel(level)

        if log_to_console:
            ch = RichHandler(
                show_time=False,
                show_level=True,
                show_path=False,
                markup=True,
                keywords=(RichHandler.KEYWORDS or []) + ["STREAM"],
                rich_tracebacks=True,
            )
            ch.setFormatter(logging.Formatter("{message}", style="{", datefmt="[%X]"))
            self.logger.addHandler(ch)

        # 文件日志输出
        if log_path:
            self.log_dir = Path(log_path)
            self.ensure_log_dir_exists(self.log_dir)

            # 使用进程ID和UUID确保文件名唯一
            process_id = os.getpid()
            unique_id = str(uuid.uuid4())[:8]
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

            log_file_name = (
                f"{self.logger.name}-{timestamp}-{process_id}-{unique_id}.log"
            )
            log_file = self.log_dir.joinpath(log_file_name)

            # 根据是否需要延迟创建选择不同的处理器
            if lazy_file_creation:
                fh = TrueLazyFileHandler(
                    str(log_file),
                    when="midnight",
                    interval=1,
                    backupCount=99,
                    encoding="utf-8",
                )
            else:
                fh = TimedRotatingFileHandler(
                    log_file,
                    when="midnight",
                    interval=1,
                    backupCount=99,
                    encoding="utf-8",
                )

            fh.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self.logger.addHandler(fh)

    @staticmethod
    def ensure_log_dir_exists(log_path: Path):
        log_path.mkdir(parents=True, exist_ok=True)

    def clean_logs(self, keep_last_n=99):
        """保留最近的n个日志文件并删除其他文件（多进程安全）"""
        if not self.log_dir:
            return

        try:
            # 获取所有日志文件，按修改时间排序
            all_logs = []
            for log_file in self.log_dir.glob("*.log"):
                try:
                    # 检查文件是否被其他进程占用
                    stat = log_file.stat()
                    # 跳过空文件（大小为0的文件）
                    if stat.st_size > 0:
                        all_logs.append((log_file, stat.st_mtime))
                    else:
                        # 直接删除空的日志文件
                        try:
                            log_file.unlink()
                        except (PermissionError, OSError):
                            pass
                except (OSError, PermissionError):
                    # 文件被占用或无法访问，跳过
                    continue

            # 按修改时间排序（最新的在后面）
            all_logs.sort(key=lambda x: x[1])

            if keep_last_n == 0:
                files_to_delete = [item[0] for item in all_logs]
            else:
                files_to_delete = [item[0] for item in all_logs[:-keep_last_n]]

            # 安全删除文件
            for log_file in files_to_delete:
                try:
                    # 双重检查文件是否还存在且可删除
                    if log_file.exists():
                        log_file.unlink()
                except (PermissionError, OSError):
                    # 文件被占用或已被其他进程删除，静默跳过
                    pass

        except Exception:
            # 清理过程中的任何异常都不应影响主程序
            pass

    def shutdown(self):
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
        self.logger.handlers.clear()
        time.sleep(1)  # 确保文件被释放


_process_logs_cleaned = False  # 添加全局变量跟踪清理状态


def log_setup(
    log_to_console=True,
    log_name="f2",
    lazy_file_creation=False,
) -> logging.Logger:
    """
    配置日志记录器（多进程安全）。

    Args:
        log_to_console (bool): 是否将日志输出到控制台，默认为 True。
        log_name (str): 日志记录器的名称，默认为 "f2"。
        lazy_file_creation (bool): 是否延迟创建日志文件，默认为 False。

    Returns:
        logging.Logger: 配置好的日志记录器实例。
    """
    global _process_logs_cleaned

    logger = logging.getLogger(log_name)
    if logger.hasHandlers():
        # logger已经被设置，不做任何操作
        return logger

    # 创建日志目录
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)

    # 初始化日志管理器
    log_manager = LogManager(log_name)
    log_manager.setup_logging(
        level=logging.INFO,
        log_to_console=log_to_console,
        log_path=log_dir,
        lazy_file_creation=lazy_file_creation,
    )

    # 只在当前进程第一次调用时清理日志文件
    if not _process_logs_cleaned:
        log_manager.clean_logs(200)
        _process_logs_cleaned = True

    return logger


# 主日志记录器（包含所有日志级别）
logger = log_setup(log_to_console=True, log_name="f2")

# 错误堆栈日志记录器（不输出到控制台，单独记录错误日志，延迟创建文件）
trace_logger = log_setup(
    log_to_console=False, log_name="f2-trace", lazy_file_creation=True
)
