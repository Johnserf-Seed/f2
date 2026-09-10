# path: tests/test_test_config.py

import pytest

import f2
from f2.utils.config.conf_manager import TestConfigManager


@pytest.fixture
def test_config_dir(tmp_path, monkeypatch):
    """把 f2.TEST_CONFIG_FILE_PATH 指向临时目录中的 test.yaml"""
    template = tmp_path / "test.yaml"
    template.write_text(
        "douyin:\n"
        "  headers:\n"
        "    Referer: https://www.douyin.com/\n"
        "  cookie: template_cookie\n"
        "bark:\n"
        "  key: ''\n"
        "  token: ''\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(f2, "TEST_CONFIG_FILE_PATH", str(template))
    monkeypatch.delenv("F2_TEST_DOUYIN_COOKIE", raising=False)
    monkeypatch.delenv("F2_TEST_BARK_KEY", raising=False)
    return tmp_path


def test_template_values_are_used_by_default(test_config_dir):
    config = TestConfigManager.get_test_config("douyin")
    assert config["cookie"] == "template_cookie"
    assert config["headers"]["Referer"] == "https://www.douyin.com/"


def test_local_file_overrides_template(test_config_dir):
    (test_config_dir / TestConfigManager.LOCAL_CONFIG_FILE_NAME).write_text(
        "douyin:\n  cookie: local_cookie\n", encoding="utf-8"
    )
    config = TestConfigManager.get_test_config("douyin")
    assert config["cookie"] == "local_cookie"
    # 未覆盖的字段保留模板值
    assert config["headers"]["Referer"] == "https://www.douyin.com/"


def test_env_overrides_local_and_template(test_config_dir, monkeypatch):
    (test_config_dir / TestConfigManager.LOCAL_CONFIG_FILE_NAME).write_text(
        "douyin:\n  cookie: local_cookie\n", encoding="utf-8"
    )
    monkeypatch.setenv("F2_TEST_DOUYIN_COOKIE", "env_cookie")
    assert TestConfigManager.get_test_config("douyin")["cookie"] == "env_cookie"


def test_empty_env_value_does_not_override(test_config_dir, monkeypatch):
    monkeypatch.setenv("F2_TEST_DOUYIN_COOKIE", "")
    assert TestConfigManager.get_test_config("douyin")["cookie"] == "template_cookie"


def test_env_only_when_template_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(f2, "TEST_CONFIG_FILE_PATH", str(tmp_path / "missing.yaml"))
    monkeypatch.setenv("F2_TEST_BARK_KEY", "env_key")
    config = TestConfigManager.get_test_config("bark")
    assert config == {"key": "env_key"}


def test_unknown_app_returns_empty_dict(test_config_dir):
    assert TestConfigManager.get_test_config("nonexistent") == {}


def test_packaged_template_has_every_app_section():
    for app in ("douyin", "tiktok", "weibo", "twitter", "bark"):
        config = TestConfigManager.get_test_config(app)
        assert (
            isinstance(config, dict) and config
        ), f"{app} section missing in test.yaml"
