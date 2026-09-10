# path: tests/test_import_side_effects.py

import importlib
import os
import random
import subprocess
import sys
import textwrap
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import pytest

import f2
from f2.log import logger as logger_module
from f2.log.logger import TrueLazyFileHandler, log_setup
from f2.utils.string import generator

REPO_ROOT = Path(f2.__file__).resolve().parents[1]

# 在干净的子进程中导入各应用模块：禁止任何 HTTP 请求，且不能创建 logs 目录或文件日志处理器
IMPORT_PROBE = textwrap.dedent(
    """
    import importlib
    import logging
    import os
    from logging.handlers import TimedRotatingFileHandler

    import httpx

    def _no_network(self, request, *args, **kwargs):
        raise AssertionError(f"导入阶段不允许发起网络请求: {request.url}")

    httpx.Client.send = _no_network
    httpx.AsyncClient.send = _no_network

    for app in ("douyin", "tiktok", "weibo", "twitter", "bark"):
        importlib.import_module(f"f2.apps.{app}.model")
    importlib.import_module("f2.apps.tiktok.utils")

    from f2.log.logger import TrueLazyFileHandler

    assert not os.path.exists("logs"), "导入 f2 不应创建 logs 目录"
    for name in ("f2", "f2-trace"):
        for handler in logging.getLogger(name).handlers:
            assert not isinstance(
                handler, (TimedRotatingFileHandler, TrueLazyFileHandler)
            ), f"导入 f2 不应给 {name} 挂载文件日志处理器"
    """
)


def _close_handlers(logger):
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
    logger_module._configured_loggers.discard(logger.name)


def test_importing_apps_has_no_network_or_filesystem_side_effects(tmp_path):
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    result = subprocess.run(
        [sys.executable, "-c", IMPORT_PROBE],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "logs").exists()


@pytest.mark.parametrize("app", ["douyin", "tiktok"])
def test_mstoken_is_fetched_once_on_first_use(monkeypatch, app):
    utils = importlib.import_module(f"f2.apps.{app}.utils")
    model = importlib.import_module(f"f2.apps.{app}.model")
    calls = []

    def fake_gen(cls):
        calls.append(1)
        return f"tok-{len(calls)}"

    monkeypatch.setattr(utils.TokenManager, "_msToken_cache", None)
    monkeypatch.setattr(utils.TokenManager, "gen_real_msToken", classmethod(fake_gen))

    # 定义模型不触发生成，实例化时才生成，且整个进程只生成一次
    assert calls == []
    first = model.BaseRequestModel()
    second = model.BaseRequestModel()
    assert first.msToken == second.msToken == "tok-1"
    assert len(calls) == 1

    if app == "douyin":
        assert model.LiveChatSend(room_id="1", content="hi").msToken == "tok-1"
    else:
        headers = utils.DeviceIdManager._device_id_headers()
        assert headers["Cookie"] == "msToken=tok-1"
    assert len(calls) == 1


def test_mstoken_failure_is_not_cached(monkeypatch):
    from f2.apps.douyin import model, utils

    attempts = []

    def flaky_gen(cls):
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("msToken 内容不符合要求")
        return "tok-ok"

    monkeypatch.setattr(utils.TokenManager, "_msToken_cache", None)
    monkeypatch.setattr(utils.TokenManager, "gen_real_msToken", classmethod(flaky_gen))

    # 失败在使用时抛出，而不是在导入时；下一次使用会重新生成
    with pytest.raises(RuntimeError):
        model.BaseRequestModel()
    assert model.BaseRequestModel().msToken == "tok-ok"
    assert len(attempts) == 2


def test_log_setup_creates_files_only_when_asked(tmp_path):
    log_dir = tmp_path / "logs"
    name = "f2-test-log-setup"

    logger = log_setup(log_to_console=False, log_name=name, log_path=str(log_dir))
    try:
        assert log_dir.is_dir()
        assert any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers)
        handler_count = len(logger.handlers)

        # 幂等：再次调用返回同一个 logger，且不会重复添加处理器
        again = log_setup(log_to_console=False, log_name=name, log_path=str(log_dir))
        assert again is logger
        assert len(logger.handlers) == handler_count
    finally:
        _close_handlers(logger)


def test_log_setup_keeps_current_process_log_file(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    stale = log_dir / "f2-old.log"
    stale.write_text("")  # 其它进程留下的空日志文件，应被清理
    name = "f2-test-keep-current"
    monkeypatch.setattr(logger_module, "_process_logs_cleaned", False)

    logger = log_setup(log_to_console=False, log_name=name, log_path=str(log_dir))
    try:
        file_handler = next(
            h for h in logger.handlers if isinstance(h, TimedRotatingFileHandler)
        )
        # 启动清理不能把本进程刚创建（还是空的）的日志文件删掉
        assert Path(file_handler.baseFilename).exists()
        assert not stale.exists()
    finally:
        _close_handlers(logger)


def test_log_setup_without_log_path_creates_no_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    name = "f2-test-console-only"

    logger = log_setup(log_to_console=True, log_name=name, log_path=None)
    try:
        assert not (tmp_path / "logs").exists()
        assert len(logger.handlers) == 1
        assert not isinstance(
            logger.handlers[0], (TimedRotatingFileHandler, TrueLazyFileHandler)
        )
    finally:
        _close_handlers(logger)


def test_generator_import_does_not_reseed_global_random():
    random.seed(1234)
    expected = random.random()

    random.seed(1234)
    importlib.reload(generator)
    assert random.random() == expected, "导入 generator 不应重置全局随机种子"


def test_gen_random_str_uses_expected_alphabet():
    value = generator.gen_random_str(32)
    assert len(value) == 32
    assert set(value) <= set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
    )
