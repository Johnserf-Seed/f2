# path: tests/test_user_config.py

import pytest

import f2
from f2.exceptions import ConfError
from f2.utils.config import user_config
from f2.utils.config.conf_manager import ConfigManager, get_f2_setting
from f2.utils.config.user_config import deep_merge, user_config_paths


@pytest.fixture
def dirs(tmp_path, monkeypatch):
    """隔离用户目录、项目目录与环境变量，不读取真实的 ~/.f2"""
    home = tmp_path / "home" / ".f2"
    project = tmp_path / "project"
    home.mkdir(parents=True)
    project.mkdir()
    monkeypatch.setattr(user_config, "user_config_dir", lambda: home)
    monkeypatch.chdir(project)
    monkeypatch.delenv("F2_CONFIG", raising=False)
    return home, project, tmp_path


def test_deep_merge_is_recursive_and_does_not_mutate():
    base = {"headers": {"User-Agent": "a", "Referer": "r"}, "list": [1, 2], "x": 1}
    override = {"headers": {"User-Agent": "b"}, "list": [3]}
    merged = deep_merge(base, override)

    assert merged == {
        "headers": {"User-Agent": "b", "Referer": "r"},
        "list": [3],
        "x": 1,
    }
    assert base["headers"]["User-Agent"] == "a"


def test_user_config_paths_order_and_filters(dirs, monkeypatch):
    home, project, tmp = dirs
    assert user_config_paths() == []

    (home / "conf.yaml").write_text("f2: {}\n", encoding="utf-8")
    (project / "conf.yaml").write_text("f2: {}\n", encoding="utf-8")
    monkeypatch.setenv("F2_CONFIG", str(tmp / "missing.yaml"))

    # 优先级从低到高：用户目录、项目目录、环境变量（后者即使不存在也返回，由读取方报错）
    assert user_config_paths() == [
        home / "conf.yaml",
        project / "conf.yaml",
        tmp / "missing.yaml",
    ]
    # 默认配置文件本身不会被当成用户配置
    assert project / "conf.yaml" not in user_config_paths(exclude=project / "conf.yaml")


def test_project_conf_overrides_without_touching_package(dirs):
    _, project, _ = dirs
    (project / "conf.yaml").write_text(
        'f2:\n  verify: false\n  douyin:\n    headers:\n      User-Agent: "mine"\n',
        encoding="utf-8",
    )

    manager = ConfigManager()
    conf = manager.get_config("f2")
    assert conf["verify"] is False
    assert conf["douyin"]["headers"]["User-Agent"] == "mine"
    # 没写的项保留默认值
    assert conf["douyin"]["headers"]["Referer"]
    # 原始配置不变，保存时不会把用户值写进包里的 conf.yaml
    assert manager.config["f2"]["verify"] is True
    assert get_f2_setting("verify") is False


def test_priority_home_then_project_then_env(dirs, monkeypatch):
    home, project, tmp = dirs
    (home / "conf.yaml").write_text(
        "f2:\n  verify: false\n  check_update: true\n", encoding="utf-8"
    )
    (project / "conf.yaml").write_text("f2:\n  verify: true\n", encoding="utf-8")
    assert get_f2_setting("verify") is True
    assert get_f2_setting("check_update") is True

    (tmp / "env.yaml").write_text("f2:\n  verify: false\n", encoding="utf-8")
    monkeypatch.setenv("F2_CONFIG", str(tmp / "env.yaml"))
    assert get_f2_setting("verify") is False


def test_app_config_files_are_not_overridden(dirs):
    _, project, _ = dirs
    (project / "conf.yaml").write_text(
        "douyin:\n  path: /user/override\n", encoding="utf-8"
    )

    app_conf = ConfigManager(f2.APP_CONFIG_FILE_PATH).get_config("douyin")
    assert app_conf.get("path") != "/user/override"


@pytest.mark.parametrize("content", ["f2: [unclosed\n", "- a\n- b\n"])
def test_invalid_user_conf_raises(dirs, content):
    _, project, _ = dirs
    (project / "conf.yaml").write_text(content, encoding="utf-8")
    with pytest.raises(ConfError):
        ConfigManager()


def test_missing_env_conf_raises(dirs, monkeypatch):
    _, _, tmp = dirs
    monkeypatch.setenv("F2_CONFIG", str(tmp / "missing.yaml"))
    with pytest.raises(ConfError):
        ConfigManager()
