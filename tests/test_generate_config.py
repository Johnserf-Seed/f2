# path: tests/test_generate_config.py

from pathlib import Path

import pytest
from ruamel.yaml import YAML

import f2
from f2.exceptions import ConfError
from f2.utils.config.conf_manager import ConfigManager, merge_missing_keys
from f2.utils.file.path import get_resource_path


def load(path: Path):
    return YAML().load(path.read_text(encoding="utf-8"))


def douyin_defaults() -> dict:
    defaults_path = Path(get_resource_path(f2.F2_DEFAULTS_FILE_PATH))
    return YAML().load(defaults_path.read_text(encoding="utf-8"))["douyin"]


@pytest.fixture
def manager():
    return ConfigManager()


def test_new_file_gets_app_defaults(manager, tmp_path):
    target = tmp_path / "sub" / "my.yaml"
    manager.generate_config("douyin", str(target))

    assert set(load(target)["douyin"]) == set(douyin_defaults())
    assert not target.with_suffix(".bak").exists()


def test_existing_file_keeps_other_apps_and_comments(manager, tmp_path):
    target = tmp_path / "my.yaml"
    original = "# 我的配置\ntiktok:\n  cookie: tk-cookie  # 保留这个注释\n"
    target.write_text(original, encoding="utf-8")

    manager.generate_config("douyin", str(target))

    text = target.read_text(encoding="utf-8")
    assert "# 我的配置" in text
    assert "# 保留这个注释" in text
    data = load(target)
    assert data["tiktok"]["cookie"] == "tk-cookie"
    assert set(data["douyin"]) == set(douyin_defaults())
    # 修改前的原文件备份为同名 .bak
    assert target.with_suffix(".bak").read_text(encoding="utf-8") == original


def test_existing_app_section_only_gets_missing_keys(manager, tmp_path):
    target = tmp_path / "my.yaml"
    target.write_text(
        "douyin:\n  cookie: my-cookie\n  path: /data/videos\n", encoding="utf-8"
    )

    manager.generate_config("douyin", str(target))

    section = load(target)["douyin"]
    assert section["cookie"] == "my-cookie"
    assert section["path"] == "/data/videos"
    assert set(section) == set(douyin_defaults())


def test_complete_file_is_left_untouched(manager, tmp_path):
    target = tmp_path / "my.yaml"
    manager.generate_config("douyin", str(target))
    before = target.read_bytes()

    manager.generate_config("douyin", str(target))

    assert target.read_bytes() == before
    assert not target.with_suffix(".bak").exists()


@pytest.mark.parametrize("content", ["douyin: [unclosed\n", "- a\n- b\n"])
def test_unreadable_file_is_not_modified(manager, tmp_path, content):
    target = tmp_path / "my.yaml"
    target.write_text(content, encoding="utf-8")

    with pytest.raises(ConfError):
        manager.generate_config("douyin", str(target))

    assert target.read_text(encoding="utf-8") == content
    assert not target.with_suffix(".bak").exists()


def test_merge_missing_keys_recurses_without_overwriting():
    target = {"headers": {"User-Agent": "mine"}, "proxies": ""}
    defaults = {
        "headers": {"User-Agent": "default", "Referer": "https://x.com/"},
        "proxies": {"http://": None},
        "timeout": 10,
    }

    assert merge_missing_keys(target, defaults) == 2
    assert target == {
        "headers": {"User-Agent": "mine", "Referer": "https://x.com/"},
        "proxies": "",
        "timeout": 10,
    }
