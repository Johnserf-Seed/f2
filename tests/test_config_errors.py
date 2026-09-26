# path: tests/test_config_errors.py

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from f2.exceptions import (
    ConfError,
    FileNotFound,
    InvalidConfError,
    InvalidEncodingError,
)
from f2.log.redact import redact_text
from f2.utils.config.conf_manager import ConfigManager, describe_yaml_error

UNCLOSED = "douyin:\n  path: [Download\n"
TAB_INDENT = "douyin:\n\tpath: Download\n"
DUPLICATE = "douyin:\n  path: a\n  path: b\n"
UNQUOTED_NAMING = "douyin:\n  path: Download\n  naming: {create}_{desc}\n"


def write(tmp_path, content, name="my.yaml"):
    path = tmp_path / name
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")
    return path


def load_error(path):
    with pytest.raises(ConfError) as exc_info:
        ConfigManager(str(path))
    return exc_info.value


# ---------------- 一行式的解析错误 ----------------


@pytest.mark.parametrize(
    "content, location",
    [
        (UNCLOSED, "第 3 行第 1 列"),
        (TAB_INDENT, "第 2 行第 1 列"),
        (DUPLICATE, "第 3 行第 3 列"),
        # 命名模板没加引号时 {create} 会被当成映射，错误指向其后的 _
        (UNQUOTED_NAMING, "第 3 行第 19 列"),
    ],
)
def test_syntax_error_is_reported_in_one_line(tmp_path, content, location):
    error = load_error(write(tmp_path, content))
    message = str(error)
    assert "配置文件解析错误" in message
    assert location in message
    assert "\n" not in message
    assert error.filepath == tmp_path / "my.yaml"


def test_duplicate_key_names_the_key(tmp_path):
    assert 'duplicate key "path"' in str(load_error(write(tmp_path, DUPLICATE)))


def test_non_utf8_file_is_explained(tmp_path):
    # 记事本以 ANSI 保存的中文配置
    content = "douyin:\n  path: 下载\n".encode("gbk")
    assert "UTF-8" in str(load_error(write(tmp_path, content)))


@pytest.mark.parametrize("content", ["- a\n- b\n", "just text\n", "123\n"])
def test_top_level_must_be_a_mapping(tmp_path, content):
    # 此前顶层是列表时会在 get_config 中抛出 AttributeError
    assert "顶层不是键值映射" in str(load_error(write(tmp_path, content)))


def test_describe_generic_error_collapses_lines():
    assert describe_yaml_error(ValueError("第一行\n  第二行")) == "第一行 第二行"


def test_missing_file_reports_given_path(tmp_path, monkeypatch):
    # 此前会退回包内目录查找，报错显示的是 site-packages 下的路径
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFound) as exc_info:
        ConfigManager("missing.yaml")
    assert exc_info.value.filepath == Path("missing.yaml")


def test_package_resources_are_still_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert ConfigManager("conf/app.yaml").get_app_config("douyin")


# ---------------- 应用的配置段 ----------------


@pytest.mark.parametrize("content", ["", "weibo:\n  path: Download\n", "douyin:\n"])
def test_missing_app_section_is_reported(tmp_path, content):
    manager = ConfigManager(str(write(tmp_path, content)))
    with pytest.raises(ConfError) as exc_info:
        manager.get_app_config("douyin")
    message = str(exc_info.value)
    assert "douyin" in message and "--init-config" in message
    assert exc_info.value.filepath == tmp_path / "my.yaml"


@pytest.mark.parametrize("content", ["douyin: [1, 2]\n", "douyin: Download\n"])
def test_app_section_must_be_a_mapping(tmp_path, content):
    manager = ConfigManager(str(write(tmp_path, content)))
    with pytest.raises(ConfError, match="不是键值映射"):
        manager.get_app_config("douyin")


def test_app_section_is_returned(tmp_path):
    manager = ConfigManager(str(write(tmp_path, "douyin:\n  path: Download\n")))
    assert manager.get_app_config("douyin") == {"path": "Download"}


# ---------------- CLI ----------------


def run_cli(tmp_path, *args, stdin=""):
    """在全新的进程里运行 CLI"""
    code = f"from f2.cli.cli_commands import main; main({list(args)!r})"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env={**os.environ, "COLUMNS": "200"},
        input=stdin,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr)
    return result.returncode, output


@pytest.mark.parametrize(
    "content, expected",
    [
        (UNCLOSED, "第 3 行第 1 列"),
        ("- a\n- b\n", "顶层不是键值映射"),
        ("weibo:\n  path: Download\n", "--init-config"),
    ],
)
def test_cli_reports_config_errors_without_traceback(tmp_path, content, expected):
    write(tmp_path, content)
    code, output = run_cli(
        tmp_path, "--no-log-file", "dy", "-c", "my.yaml", "-M", "one", "-u", "x"
    )
    assert code == 1
    assert expected in output
    assert "Traceback" not in output


def test_cli_update_config_accepts_file_without_app_section(tmp_path):
    # --update-config 本来就用于写入新的配置段，不应要求文件里已有这一段
    write(tmp_path, "weibo:\n  path: Download\n")
    code, output = run_cli(
        tmp_path,
        "--no-log-file",
        "dy",
        "-c",
        "my.yaml",
        "--update-config",
        "-M",
        "one",
        stdin="n\n",
    )
    assert code == 0, output
    assert "Traceback" not in output


# ---------------- 报错中的配置项与脱敏 ----------------

# 低熵的假值，避免被 gitleaks 当成真实密钥
SECRET = "f2" * 8
COOKIE = f"sid_tt={SECRET}; sessionid={SECRET}"


def test_setting_name_survives_log_redaction():
    error = ConfError(
        "日期区间参数格式错误，请查阅文档后重试",
        key="interval",
        value="2024-13-01|2024-12-31",
    )
    message = str(error)
    assert "Setting: interval" in message
    assert "Value: 2024-13-01|2024-12-31" in message
    # 此前标签为 Key，日志脱敏会把配置项名称 interval 当成密钥打码
    assert redact_text(message) == message


@pytest.mark.parametrize(
    "error",
    [
        ConfError("配置有误", key="cookie", value=COOKIE),
        InvalidEncodingError(key="cookie", value=COOKIE),
        InvalidConfError(key="token", value=COOKIE),
    ],
)
def test_sensitive_values_are_masked(error):
    # 此前被打码的是键名，Value 中的 cookie 反而原样输出
    message = str(error)
    assert SECRET not in message
    assert "Setting: " in message
    assert redact_text(message) == message


def test_invalid_conf_error_lists_setting_and_value():
    message = str(InvalidConfError(key="naming", value="{create}"))
    assert message.endswith(" | Setting: naming | Value: {create}")


def test_invalid_conf_error_without_value():
    assert str(InvalidConfError(key="naming", value="")) == (
        "请检查配置文件格式是否正确: naming 不能为空，使用默认配置"
    )


def test_cli_shows_setting_name(tmp_path):
    code, output = run_cli(
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
    assert code == 1
    assert "Setting: interval" in output
    assert "***" not in output
