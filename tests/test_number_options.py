# path: tests/test_number_options.py

import os
import re
import subprocess
import sys

import pytest

from f2.crawlers.base_crawler import BaseCrawler
from f2.exceptions import ConfError
from f2.utils.config.merge import check_number_options


@pytest.mark.parametrize(
    "conf, expected",
    [
        ({"max_tasks": 5, "timeout": 10}, {"max_tasks": 5, "timeout": 10}),
        # 配置文件中写成字符串的数字
        ({"max_tasks": "5", "timeout": "2.5"}, {"max_tasks": 5, "timeout": 2.5}),
        ({"max_retries": 3.0}, {"max_retries": 3}),
        # max_counts 为 0 或 None 表示不限制
        ({"max_counts": 0}, {"max_counts": 0}),
        (
            {"max_counts": None, "page_counts": 20},
            {"max_counts": None, "page_counts": 20},
        ),
        ({}, {}),
    ],
)
def test_valid_number_options(conf, expected):
    assert check_number_options(dict(conf)) == expected


@pytest.mark.parametrize(
    "conf",
    [
        {"max_tasks": 0},
        {"max_tasks": -1},
        {"max_connections": 0},
        {"max_retries": 0},
        {"timeout": 0},
        {"page_counts": 0},
        {"max_counts": -1},
        {"max_tasks": "abc"},
        {"max_tasks": True},
        {"max_retries": 2.5},
    ],
)
def test_invalid_number_options(conf):
    [name] = conf
    with pytest.raises(ConfError, match=name):
        check_number_options(dict(conf))


def test_zero_max_tasks_is_rejected_before_downloads_hang():
    # 此前 max_tasks 为 0 时下载一直等待信号量、程序卡住；为负数时报 Semaphore 的 ValueError。
    # 测试中常用 timeout 为 0 跳过翻页等待，BaseCrawler 只检查这几项
    with pytest.raises(ConfError, match="max_tasks"):
        BaseCrawler({"max_tasks": 0})


def run_cli(tmp_path, *args, input=None):
    code = f"from f2.cli.cli_commands import main; main({list(args)!r})"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env={**os.environ, "COLUMNS": "200"},
        capture_output=True,
        text=True,
        input=input,
        timeout=120,
    )
    return result.returncode, re.sub(
        r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr
    )


@pytest.mark.parametrize(
    "app, url",
    [
        ("dy", "https://www.douyin.com/user/x"),
        ("tk", "https://www.tiktok.com/@x"),
        ("x", "https://x.com/NASA"),
        ("wb", "https://weibo.com/u/1234567890"),
    ],
)
def test_cli_reports_invalid_numbers_before_requests(tmp_path, app, url):
    code, output = run_cli(
        tmp_path, "--no-log-file", app, "-M", "post", "-u", url, "--max-tasks", "0"
    )
    assert code == 1
    assert "max_tasks" in output
    assert "Traceback" not in output


def test_base_crawler_allows_zero_timeout_for_library_use():
    # timeout 由命令行检查；作为库使用时（如测试中跳过翻页等待）仍可为 0
    BaseCrawler({"timeout": 0})


def test_update_config_does_not_write_invalid_numbers(tmp_path):
    # 此前 --update-config 不经检查就把 0 写进配置文件，之后每次运行都失败
    config = tmp_path / "my.yaml"
    config.write_text("douyin:\n  max_tasks: 5\n", encoding="utf-8")

    code, output = run_cli(
        tmp_path,
        "--no-log-file",
        "dy",
        "-c",
        str(config),
        "--update-config",
        "--max-tasks",
        "0",
        # 写回前会询问是否更新，这里确认
        input="y\n",
    )

    assert code == 1
    assert "max_tasks" in output
    assert "Traceback" not in output
    assert "max_tasks: 5" in config.read_text(encoding="utf-8")
