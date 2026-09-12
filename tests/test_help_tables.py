# path: tests/test_help_tables.py

import importlib

import click
import pytest

# 每个应用：click 命令名 与 富文本帮助模块
APPS = {
    "douyin": "douyin",
    "tiktok": "tiktok",
    "twitter": "twitter",
    "weibo": "weibo",
    "bark": "bark",
}


def _long_options(command: click.Command) -> set:
    names = set()
    for param in command.params:
        if isinstance(param, click.Option) and not param.hidden:
            names.update(opt for opt in param.opts if opt.startswith("--"))
    names.discard("--help")
    return names


@pytest.mark.parametrize("app", sorted(APPS))
def test_rich_help_lists_every_cli_option(app, capsys, monkeypatch):
    """-h 的富文本帮助表由 help.py 手工维护，必须包含 cli.py 上定义的全部长选项"""
    monkeypatch.setenv(
        "COLUMNS", "500"
    )  # 非终端下 rich 默认 80 列，会把选项列裁成省略号
    command = getattr(importlib.import_module(f"f2.apps.{app}.cli"), APPS[app])
    importlib.import_module(f"f2.apps.{app}.help").help()
    rich_help = capsys.readouterr().out

    missing = sorted(opt for opt in _long_options(command) if opt not in rich_help)
    assert not missing, f"{app} 的富文本帮助缺少选项: {missing}"
