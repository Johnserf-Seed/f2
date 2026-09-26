# path: tests/test_cli_logging.py

import logging
import os
import re
import subprocess
import sys

import pytest

from f2.cli.cli_commands import file_logging_disabled
from f2.log.logger import log_setup


@pytest.mark.parametrize(
    "args, expected",
    [
        (["--no-log-file", "dy", "-M", "one"], True),
        (["-d", "DEBUG", "--no-log-file", "dy"], True),
        (["--debug", "DEBUG", "-l", "en_US", "--no-log-file", "dy"], True),
        (["--no-log-file", "--version"], True),
        ([], False),
        (["dy", "-M", "one"], False),
        # 写在应用名之后的参数属于应用命令，由 click 报错
        (["dy", "--no-log-file"], False),
        # -d 的值不能被当成开关
        (["-d", "--no-log-file"], False),
    ],
)
def test_file_logging_disabled(args, expected):
    assert file_logging_disabled(args) is expected


def run_cli(tmp_path, *args):
    """在全新的进程和空目录里运行 CLI，避免日志配置在测试之间残留"""
    code = f"from f2.cli.cli_commands import main; main({list(args)!r})"
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        # 子进程不是终端，rich 默认按 80 列排版会截断帮助表
        env={**os.environ, "COLUMNS": "200"},
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_cli_writes_log_files_by_default(tmp_path):
    result = run_cli(tmp_path, "--version")
    assert result.returncode == 0
    assert (tmp_path / "logs").is_dir()


@pytest.mark.parametrize(
    "args",
    [
        ("--no-log-file", "--version"),
        ("-d", "DEBUG", "--no-log-file", "--version"),
    ],
)
def test_no_log_file_skips_log_directory(tmp_path, args):
    # #293：没有写文件权限的环境不能创建 logs 目录
    result = run_cli(tmp_path, *args)
    assert result.returncode == 0
    assert not (tmp_path / "logs").exists()


def test_root_help_lists_no_log_file(tmp_path):
    result = run_cli(tmp_path, "--no-log-file", "-h")
    assert result.returncode == 0
    plain = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)  # 去掉颜色控制符
    assert "--no-log-file" in plain
    assert not (tmp_path / "logs").exists()


def test_no_log_file_keeps_traceback_out_of_console(tmp_path):
    # 没有日志文件时错误堆栈应被丢弃，此前会经 logging.lastResort 打印到控制台
    result = run_cli(
        tmp_path,
        "--no-log-file",
        "wb",
        "-M",
        "post",
        "-u",
        "https://weibo.com/u/2265830070",
        "-i",
        "2024-13-01|2024-12-31",
    )
    output = result.stdout + result.stderr
    assert result.returncode == 1
    assert "2024-13-01|2024-12-31" in output
    assert "Traceback" not in output
    assert not (tmp_path / "logs").exists()


def test_log_setup_without_outputs_discards_records():
    log = log_setup(log_to_console=False, log_name="f2-test-silent", log_path=None)
    assert [type(h) for h in log.handlers] == [logging.NullHandler]
