# path: tests/test_naming_fields.py

import importlib

import click
import pytest

APPS = ["douyin", "tiktok", "twitter", "weibo"]
# 各应用命名模板中出现过的字段
CANDIDATES = [
    "create",
    "nickname",
    "uniqueId",
    "aweme_id",
    "tweet_id",
    "weibo_id",
    "desc",
    "caption",
    "uid",
]


def supported_fields(app):
    """format_file_name 能够填充的字段"""
    utils = importlib.import_module(f"f2.apps.{app}.utils")
    fields = []
    for name in CANDIDATES:
        try:
            # TikTok 的作品数据为空时直接报错，给一个最小的作品
            utils.format_file_name("{" + name + "}", {"aweme_id": "1"})
        except KeyError:
            continue
        fields.append(name)
    return fields


@pytest.mark.parametrize("app", APPS)
def test_cli_accepts_every_field_the_formatter_supports(app):
    # 抖音的 {caption} 写在配置文件里可以用，命令行 --naming 却报“不符合命名模式”
    cli = importlib.import_module(f"f2.apps.{app}.cli")
    ctx = click.Context(click.Command(app))

    fields = supported_fields(app)
    assert {"create", "desc"} <= set(fields)
    for name in fields:
        template = "{create}_{" + name + "}"
        assert cli.handler_naming(ctx, None, template) == template


@pytest.mark.parametrize("app", APPS)
def test_cli_rejects_unknown_fields(app):
    cli = importlib.import_module(f"f2.apps.{app}.cli")
    ctx = click.Context(click.Command(app))

    with pytest.raises(click.BadParameter):
        cli.handler_naming(ctx, None, "{create}_{unknown}")
