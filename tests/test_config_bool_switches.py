# path: tests/test_config_bool_switches.py

import importlib
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

import f2
from f2.apps.bark.utils import ClientConfManager as BarkClientConfManager
from f2.exceptions.conf_exceptions import ConfError
from f2.utils.config import conf_manager
from f2.utils.config.merge import coerce_bool_options, parse_bool

APPS = ["douyin", "tiktok", "twitter", "weibo"]
PACKAGE_APP_CONF = Path(f2.__file__).parent / f2.APP_CONFIG_FILE_PATH


def load(app):
    module = importlib.import_module(f"f2.apps.{app}.cli")
    return module, getattr(module, app)


def bool_option_names(command):
    return [
        param.name
        for param in command.params
        if isinstance(param.type, click.types.BoolParamType)
    ]


@pytest.mark.parametrize(
    "value, expected",
    [
        ("yes", True),
        ("No", False),
        (" on ", True),
        ("off", False),
        ("true", True),
        ("0", False),
        (True, True),
        (False, False),
        # 无法识别的值原样返回，例如 verify 可以是 CA 证书路径
        ("/etc/ssl/ca.pem", "/etc/ssl/ca.pem"),
        (None, None),
        (5, 5),
    ],
)
def test_parse_bool(value, expected):
    assert parse_bool(value) == expected


@pytest.mark.parametrize("app", APPS)
def test_bool_options_in_config_are_converted(app):
    # ruamel.yaml 按 YAML 1.2 把 yes/no 读成字符串，此前 "no" 为真，写成 no 的开关反而打开
    _, command = load(app)
    names = bool_option_names(command)
    assert "folderize" in names

    off = coerce_bool_options(command.params, {name: "no" for name in names})
    on = coerce_bool_options(command.params, {name: "yes" for name in names})

    assert off == {name: False for name in names}
    assert on == {name: True for name in names}


def test_unknown_switch_value_is_a_config_error():
    _, command = load("douyin")

    with pytest.raises(ConfError) as exc_info:
        coerce_bool_options(command.params, {"cover": "maybe"})

    assert exc_info.value.key == "cover"


@pytest.fixture
def custom_conf(tmp_path, monkeypatch):
    """抖音命令读取的自定义配置，并截取合并后交给 set_cli_config 的参数"""
    original = PACKAGE_APP_CONF.read_bytes()
    module, command = load("douyin")
    captured = {}
    monkeypatch.setattr(
        module, "set_cli_config", lambda **kwargs: captured.update(kwargs)
    )

    def invoke(text):
        path = tmp_path / "my.yaml"
        path.write_text(text, encoding="utf-8")
        args = ["-c", str(path), "-M", "post", "-u", "https://www.douyin.com/user/x"]
        return CliRunner().invoke(command, args), captured

    yield invoke
    assert PACKAGE_APP_CONF.read_bytes() == original


def test_douyin_cli_reads_yes_no_switches(custom_conf):
    outcome, kwargs = custom_conf(
        "douyin:\n"
        "  cookie: a=b\n"
        "  folderize: no\n"
        "  cover: no\n"
        "  desc: yes\n"
        "  music: off\n"
        "  lyric: 'no'\n"
    )

    assert outcome.exit_code == 0, outcome.output
    assert [kwargs[k] for k in ("folderize", "cover", "desc", "music", "lyric")] == [
        False,
        False,
        True,
        False,
        False,
    ]


def test_douyin_cli_rejects_unknown_switch_value(custom_conf):
    outcome, _ = custom_conf("douyin:\n  cookie: a=b\n  cover: maybe\n")

    assert isinstance(outcome.exception, ConfError)
    assert outcome.exception.key == "cover"


@pytest.mark.parametrize("value, expected", [("no", False), ("yes", True)])
def test_enable_bark_reads_yes_no(monkeypatch, value, expected):
    # 此前 enable_bark: no 会打开 Bark 通知
    monkeypatch.setattr(BarkClientConfManager, "client_conf", {"enable_bark": value})

    assert BarkClientConfManager.enable_bark() is expected


@pytest.mark.parametrize(
    "value, expected", [("no", False), ("yes", True), ("ca.pem", "ca.pem")]
)
def test_f2_setting_reads_yes_no(monkeypatch, value, expected):
    class FakeConfigManager:
        def __init__(self, *args, **kwargs):
            pass

        def get_config(self, app):
            return {"verify": value}

    monkeypatch.setattr(conf_manager, "ConfigManager", FakeConfigManager)

    assert conf_manager.get_f2_setting("verify", True) == expected
