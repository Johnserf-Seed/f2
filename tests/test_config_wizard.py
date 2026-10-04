# path: tests/test_config_wizard.py

import importlib

import pytest
from click.testing import CliRunner

import f2
import f2.conf.config_wizard as wizard_module
from f2.cli.wizard_command import config_wizard_command
from f2.conf.config_wizard import ConfigWizard

APPS = ["douyin", "tiktok", "weibo", "twitter"]
# 各应用作品数据中命名用到的字段
SAMPLE = {
    "create_time": "2026-10-04 12-00-00",
    "createTime": "2026-10-04 12-00-00",
    "tweet_created_at": "2026-10-04 12-00-00",
    "weibo_created_at": "2026-10-04 12-00-00",
    "nickname": "alice",
    "aweme_id": "7000000000000000000",
    "tweet_id": "1800000000000000000",
    "weibo_id": "5000000000000000",
    "desc": "文案",
    "tweet_desc": "文案",
    "weibo_desc": "文案",
    "uid": "1",
    "user_unique_id": "alice",
}


@pytest.fixture
def home(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    return tmp_path


@pytest.mark.parametrize("app", APPS)
def test_wizard_offers_the_cli_modes(app):
    modes = ConfigWizard().app_info[app]["modes"]

    assert modes == getattr(f2, f"{app.upper()}_MODE_LIST")
    # 每个模式都有说明，此前 related、search 只显示模式名
    assert all(ConfigWizard()._get_mode_description(mode) != mode for mode in modes)


@pytest.mark.parametrize(
    "app, template",
    [
        (app, template)
        for app, templates in ConfigWizard.naming_templates().items()
        for template, _ in templates
        if template != "custom"
    ],
)
def test_naming_templates_use_existing_fields(app, template):
    # 此前推特的 {user_name}_{create} 在下载时报“文件名模板字段不存在”
    utils = importlib.import_module(f"f2.apps.{app}.utils")

    assert utils.format_file_name(template, SAMPLE)


def fake_wizard(monkeypatch, asked):
    def must_not_ask(*args, **kwargs):
        asked.append(args)
        raise AssertionError("不应再询问")

    monkeypatch.setattr(ConfigWizard, "show_welcome", lambda self: None)
    monkeypatch.setattr(ConfigWizard, "select_apps", must_not_ask)
    monkeypatch.setattr(
        ConfigWizard, "configure_app", lambda self, app: {"url": "u", "mode": "post"}
    )
    monkeypatch.setattr(ConfigWizard, "preview_config", lambda self, data: True)
    monkeypatch.setattr(wizard_module.Prompt, "ask", must_not_ask)


def test_cli_output_and_app_are_used(monkeypatch, tmp_path):
    # 此前 -o 与 -a 只被打印出来，向导仍然询问要配置的应用与保存路径
    asked = []
    fake_wizard(monkeypatch, asked)
    output = tmp_path / "my_config.yaml"

    result = CliRunner().invoke(
        config_wizard_command, ["-o", str(output), "-a", "twitter"]
    )

    assert result.exit_code == 0, result.output
    assert asked == []
    assert output.read_text(encoding="utf-8").count("twitter:") == 1


def test_cli_rejects_an_unknown_app():
    result = CliRunner().invoke(config_wizard_command, ["-a", "bilibili"])

    assert result.exit_code == 2


def test_output_path_expands_home(monkeypatch, home):
    fake_wizard(monkeypatch, [])

    assert ConfigWizard().run("~/configs/f2.yaml", ["douyin"])
    assert (home / "configs" / "f2.yaml").is_file()


def test_wizard_stops_when_input_ends(monkeypatch, tmp_path):
    # 此前输入结束（例如在管道中运行）时，各输入循环吞掉 EOFError 并无限重试
    calls = []

    def end_of_input(*args, **kwargs):
        calls.append(args)
        if len(calls) > 100:
            raise SystemExit("输入循环没有停止")
        raise EOFError

    monkeypatch.setattr(ConfigWizard, "show_welcome", lambda self: None)
    monkeypatch.setattr("rich.console.Console.input", end_of_input)

    assert ConfigWizard().run(str(tmp_path / "f2.yaml"), ["douyin"]) is False
    assert len(calls) == 1
    assert not (tmp_path / "f2.yaml").exists()
