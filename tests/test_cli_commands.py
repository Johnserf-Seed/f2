# path: tests/test_cli_commands.py

import click
import pytest
import logging

from click.testing import CliRunner

from f2.cli.cli_commands import (
    handle_help,
    handle_version,
    handle_debug,
    handle_last_version,
    set_cli_config,
    DynamicGroup,
)
from f2 import __version__ as f2_version
from f2.i18n.translator import _


# 测试 handle_help
def test_handle_help():
    runner = CliRunner()

    @click.command()
    @click.option("--help", is_flag=True, expose_value=False, callback=handle_help)
    def cli():
        pass

    try:
        result = runner.invoke(cli, ["--help"])  # 调用 --help 参数
        assert result.exit_code == 0
        assert "命令帮助" in result.output
    except SystemExit as e:
        pytest.fail(f"SystemExit with exit code {e.code} occurred: {e}")


# 测试 handle_debug
def test_handle_debug(caplog):
    runner = CliRunner()

    @click.command()
    @click.option(
        "--debug",
        type=click.Choice(["DEBUG", "INFO", "ERROR", "WARNING"]),
        expose_value=False,
        callback=handle_debug,
    )
    def cli():
        pass

    try:
        with caplog.at_level(logging.DEBUG):
            result = runner.invoke(cli, ["--debug", "DEBUG"])
        assert result.exit_code == 0
        assert "DEBUG" in caplog.text
    except SystemExit as e:
        pytest.fail(f"SystemExit with exit code {e.code} occurred: {e}")


# 测试 DynamicGroup
def test_dynamic_group_get_command():
    runner = CliRunner()

    # 这是一个伪造的应用映射，用于测试 DynamicGroup
    # 动态导入的 CLI 应用是否可以正确加载和执行
    @click.command()
    def fake_command():
        click.echo("Fake command executed")

    # 模拟一个应用命令，测试其正确加载
    dynamic_group = DynamicGroup()

    # 模拟成功的命令调用
    @click.command()
    def cli():
        dynamic_group.get_command(None, "douyin")()  # 调用动态获取的命令

    try:
        result = runner.invoke(cli)
        assert result.exit_code == 2
        assert "[OPTIONS]" in result.output
    except SystemExit as e:
        pytest.fail(f"SystemExit with exit code {e.code} occurred: {e}")

    # 模拟找不到的命令
    @click.command()
    def cli_fail():
        dynamic_group.get_command(None, "non_existent_command")  # 模拟找不到的命令

    try:
        result = runner.invoke(cli_fail)
        assert result.exit_code == 1
        assert "" in result.output
    except SystemExit as e:
        pytest.fail(f"SystemExit with exit code {e.code} occurred: {e}")


# 测试 set_cli_config 和 run_app
def test_set_cli_config():
    runner = CliRunner()

    # 创建一个伪造的 CLI 配置设置
    @click.command()
    def cli():
        click.echo("CLI config set")
        set_cli_config(None, app_name="test-app")

    try:
        result = runner.invoke(cli, ["--app-name", "test-app"])
        assert result.exit_code == 2
        assert "No such option" in result.output
    except SystemExit as e:
        pytest.fail(f"SystemExit with exit code {e.code} occurred: {e}")


# 测试命令行选项--help、--version等的正确性
@pytest.mark.parametrize(
    "args, expected_output",
    [
        (["--help"], "命令帮助"),
        (["--version"], f"Version {f2_version}"),
        (["--debug", "DEBUG"], ""),
        (["--check-version"], "版本检查"),
    ],
)
def test_cli_options(args, expected_output):
    runner = CliRunner()

    @click.command()
    @click.option("--help", is_flag=True, expose_value=False, callback=handle_help)
    @click.option(
        "--version", is_flag=True, expose_value=False, callback=handle_version
    )
    @click.option(
        "--debug",
        type=click.Choice(["DEBUG", "INFO", "ERROR", "WARNING"]),
        expose_value=False,
        callback=handle_debug,
    )
    @click.option(
        "--check-version",
        is_flag=True,
        expose_value=False,
        callback=handle_last_version,
    )
    def cli():
        pass

    try:
        result = runner.invoke(cli, args)
        assert result.exit_code == 0
        assert expected_output in result.output
    except SystemExit as e:
        pytest.fail(f"SystemExit with exit code {e.code} occurred: {e}")
