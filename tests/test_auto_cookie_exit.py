# path: tests/test_auto_cookie_exit.py

import importlib
from pathlib import Path

import pytest
from click.testing import CliRunner

import f2

APPS = ["douyin", "tiktok", "twitter", "weibo"]
PACKAGE_APP_CONF = Path(f2.__file__).parent / f2.APP_CONFIG_FILE_PATH


def load(app):
    module = importlib.import_module(f"f2.apps.{app}.cli")
    return module, getattr(module, app)


def fake_browser(monkeypatch, module, result):
    """替换读取浏览器 cookie 的函数，测试不会接触真实的浏览器"""

    def get_cookie_from_browser(browser, domain):
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(module, "get_cookie_from_browser", get_cookie_from_browser)


@pytest.fixture
def conf(tmp_path, monkeypatch):
    """自定义配置文件；默认路径也指向它，保证不会改写包内的 app.yaml"""
    original = PACKAGE_APP_CONF.read_bytes()
    path = tmp_path / "my.yaml"
    path.write_text("douyin:\n  path: Download\n", encoding="utf-8")
    for app in APPS:
        monkeypatch.setattr(
            load(app)[0], "get_resource_path", lambda *args, **kwargs: path
        )
    yield path
    assert PACKAGE_APP_CONF.read_bytes() == original


@pytest.mark.parametrize("app", APPS)
@pytest.mark.parametrize(
    "result",
    [RuntimeError("无法解密 cookie"), {}, PermissionError("cookie 数据库被占用")],
)
def test_auto_cookie_failure_exits_with_1(monkeypatch, conf, app, result):
    # 此前 finally 中的 ctx.exit(0) 会覆盖 abort，获取失败时退出码仍为 0
    module, command = load(app)
    fake_browser(monkeypatch, module, result)
    outcome = CliRunner().invoke(command, ["--auto-cookie", "chrome"])
    assert outcome.exit_code == 1


@pytest.mark.parametrize("app", APPS)
def test_auto_cookie_success_updates_config(monkeypatch, conf, app):
    module, command = load(app)
    fake_browser(monkeypatch, module, {"sessionid": "f2f2"})
    outcome = CliRunner().invoke(
        command, ["-c", str(conf), "--auto-cookie", "chrome"], input="y\n"
    )
    assert outcome.exit_code == 0, outcome.output
    assert "sessionid=f2f2" in conf.read_text(encoding="utf-8")


@pytest.mark.parametrize("app", APPS)
@pytest.mark.parametrize("answer, exit_code", [("n\n", 0), ("", 1)])
def test_auto_cookie_confirmation(monkeypatch, conf, app, answer, exit_code):
    # 选择不更新属于正常结束；输入结束（EOF）时 click.confirm 抛出 Abort，以退出码 1 结束
    module, command = load(app)
    fake_browser(monkeypatch, module, {"sessionid": "f2f2"})
    before = conf.read_text(encoding="utf-8")
    outcome = CliRunner().invoke(
        command, ["-c", str(conf), "--auto-cookie", "chrome"], input=answer
    )
    assert outcome.exit_code == exit_code, outcome.output
    assert conf.read_text(encoding="utf-8") == before
