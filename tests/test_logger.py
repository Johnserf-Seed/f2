import pytest
import logging
from pathlib import Path
from f2.log.logger import LogManager

LOG_DIR = Path("./test_logs")


@pytest.fixture(scope="function")
def log_manager():
    # 创建临时的日志目录
    LOG_DIR.mkdir(exist_ok=True)

    # 初始化日志管理器
    manager = LogManager()
    manager.setup_logging(level=logging.DEBUG, log_to_console=False, log_path=LOG_DIR)

    # 记录一些测试日志
    logger = manager.logger
    logger.debug("Test debug message")
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")

    yield manager, LOG_DIR

    # 清理操作
    manager.shutdown()
    for log_file in LOG_DIR.iterdir():
        log_file.unlink()
    LOG_DIR.rmdir()


def test_log_file_creation(log_manager):
    _, temp_log_dir = log_manager
    # 测试是否已经在指定的目录中创建了日志文件
    log_files = list(temp_log_dir.glob("*.log"))
    assert len(log_files) == 1


def test_clean_logs(log_manager):
    manager, temp_log_dir = log_manager
    # 写入一些测试日志文件
    for _ in range(10):
        manager.logger.debug("debug message")
        manager.logger.info("info message")
    # 清理所有日志
    manager.clean_logs(keep_last_n=3)
    log_files = list(temp_log_dir.glob("*.log"))
    assert len(log_files) == 1
