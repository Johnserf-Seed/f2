# path: tests/test_user_folder_rename.py

import logging
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from f2.apps.douyin import utils as douyin_utils
from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok import utils as tiktok_utils
from f2.apps.tiktok.db import AsyncUserDB as TiktokUserDB
from f2.apps.twitter import utils as twitter_utils
from f2.apps.weibo import utils as weibo_utils
from f2.utils.file.path import migrate_user_folder
from f2.utils.string.formatter import replaceT

# (应用名, utils 模块, 本地用户记录中保存目录名的字段)
APPS = [
    pytest.param("douyin", douyin_utils, "nickname", id="douyin"),
    pytest.param("tiktok", tiktok_utils, "uniqueId", id="tiktok"),
    pytest.param("twitter", twitter_utils, "nickname", id="twitter"),
    pytest.param("weibo", weibo_utils, "nickname", id="weibo"),
]

# 目录名是经过 replaceT 处理的昵称的应用
NICKNAME_APPS = [app for app in APPS if app.values[2] == "nickname"]


@pytest.fixture
def kwargs(tmp_path):
    return {"path": str(tmp_path / "Download"), "mode": "post"}


def user_folder(tmp_path, app, name, mode="post"):
    return (tmp_path / "Download" / app / mode / name).resolve()


def make_folder(path, files=("video.mp4",)):
    path.mkdir(parents=True)
    for name in files:
        (path / name).write_text(name, encoding="utf-8")
    return path


def f2_messages(caplog, level):
    return [
        r.getMessage() for r in caplog.records if r.name == "f2" and r.levelno == level
    ]


@pytest.mark.parametrize("app, utils, key", APPS)
def test_renames_old_folder_and_keeps_files(tmp_path, kwargs, caplog, app, utils, key):
    old = make_folder(user_folder(tmp_path, app, "old_name"))
    make_folder(old / "2024-01-01_desc", files=("2024-01-01_desc-cover.jpg",))

    with caplog.at_level(logging.INFO):
        user_path = utils.create_or_rename_user_folder(
            kwargs, {key: "old_name"}, "new_name"
        )

    assert user_path == user_folder(tmp_path, app, "new_name")
    assert not old.exists()
    assert (user_path / "video.mp4").read_text(encoding="utf-8") == "video.mp4"
    assert (user_path / "2024-01-01_desc" / "2024-01-01_desc-cover.jpg").is_file()
    assert any(str(old) in m for m in f2_messages(caplog, logging.INFO))


@pytest.mark.parametrize("app, utils, key", APPS)
def test_keeps_both_folders_when_new_folder_exists(
    tmp_path, kwargs, caplog, app, utils, key
):
    old = make_folder(user_folder(tmp_path, app, "old_name"), files=("old.mp4",))
    new = make_folder(user_folder(tmp_path, app, "new_name"), files=("new.mp4",))

    with caplog.at_level(logging.INFO):
        user_path = utils.create_or_rename_user_folder(
            kwargs, {key: "old_name"}, "new_name"
        )

    # 不覆盖也不合并：两个目录的内容都保持原样，之后下载到新目录
    assert user_path == new
    assert sorted(os.listdir(old)) == ["old.mp4"]
    assert sorted(os.listdir(new)) == ["new.mp4"]
    warnings = f2_messages(caplog, logging.WARNING)
    assert len(warnings) == 1
    assert str(old) in warnings[0] and str(new) in warnings[0]


@pytest.mark.parametrize("local_user_data", [{}, None])
@pytest.mark.parametrize("app, utils, key", APPS)
def test_creates_folder_without_local_record(
    tmp_path, kwargs, caplog, app, utils, key, local_user_data
):
    with caplog.at_level(logging.INFO):
        user_path = utils.create_or_rename_user_folder(
            kwargs, local_user_data, "new_name"
        )

    assert user_path == user_folder(tmp_path, app, "new_name")
    assert user_path.is_dir()
    assert os.listdir(user_path.parent) == ["new_name"]
    assert f2_messages(caplog, logging.WARNING) == []


@pytest.mark.parametrize("app, utils, key", APPS)
def test_same_name_uses_existing_folder(tmp_path, kwargs, app, utils, key):
    folder = make_folder(user_folder(tmp_path, app, "name"))

    user_path = utils.create_or_rename_user_folder(kwargs, {key: "name"}, "name")

    assert user_path == folder
    assert (folder / "video.mp4").is_file()


@pytest.mark.parametrize("app, utils, key", APPS)
def test_creates_new_folder_when_old_folder_is_missing(
    tmp_path, kwargs, caplog, app, utils, key
):
    with caplog.at_level(logging.INFO):
        user_path = utils.create_or_rename_user_folder(
            kwargs, {key: "old_name"}, "new_name"
        )

    assert user_path == user_folder(tmp_path, app, "new_name")
    assert os.listdir(user_path.parent) == ["new_name"]
    assert f2_messages(caplog, logging.WARNING) == []


@pytest.mark.parametrize("app, utils, key", APPS)
def test_later_runs_after_rename_are_quiet(tmp_path, kwargs, caplog, app, utils, key):
    # 本地记录里仍是旧名称，之后每次运行都会再比较一次，不能反复提示或改动目录
    make_folder(user_folder(tmp_path, app, "old_name"))
    utils.create_or_rename_user_folder(kwargs, {key: "old_name"}, "new_name")
    caplog.clear()

    with caplog.at_level(logging.INFO):
        user_path = utils.create_or_rename_user_folder(
            kwargs, {key: "old_name"}, "new_name"
        )

    assert user_path == user_folder(tmp_path, app, "new_name")
    assert (user_path / "video.mp4").is_file()
    assert f2_messages(caplog, logging.WARNING) == []
    assert f2_messages(caplog, logging.INFO) == []


@pytest.mark.parametrize("app, utils, key", APPS)
def test_only_the_current_mode_is_renamed(tmp_path, kwargs, app, utils, key):
    other_mode = make_folder(user_folder(tmp_path, app, "old_name", mode="like"))

    user_path = utils.create_or_rename_user_folder(
        kwargs, {key: "old_name"}, "new_name"
    )

    assert user_path == user_folder(tmp_path, app, "new_name")
    assert os.listdir(user_path) == []
    assert (other_mode / "video.mp4").is_file()


@pytest.mark.parametrize("app, utils, key", APPS)
def test_default_relative_path_matches_create_user_folder(
    tmp_path, monkeypatch, app, utils, key
):
    # 未配置 path 时相对当前目录的 Download，新旧目录的算法与 create_user_folder 一致
    monkeypatch.chdir(tmp_path)
    kwargs = {"mode": "one"}
    old = make_folder(user_folder(tmp_path, app, "old_name", mode="one"))

    user_path = utils.create_or_rename_user_folder(
        kwargs, {key: "old_name"}, "new_name"
    )

    assert user_path == utils.create_user_folder(kwargs, "new_name")
    assert user_path == user_folder(tmp_path, app, "new_name", mode="one")
    assert (user_path / "video.mp4").is_file()
    assert not old.exists()
    with pytest.raises(TypeError):
        utils.create_user_folder(["not", "a", "dict"], "new_name")


@pytest.mark.parametrize("app, utils, key", NICKNAME_APPS)
def test_folder_follows_new_nickname_rule(tmp_path, kwargs, app, utils, key):
    # 旧版本把 emoji 等字符替换成下划线存入数据库，升级后当前昵称保留原字符（#248）
    old = make_folder(user_folder(tmp_path, app, "于哲金_"))

    user_path = utils.create_or_rename_user_folder(
        kwargs, {key: "于哲金_"}, replaceT("于哲金🫂")
    )

    assert user_path == user_folder(tmp_path, app, "于哲金🫂")
    assert (user_path / "video.mp4").is_file()
    assert not old.exists()


def test_case_only_change_is_renamed(tmp_path):
    # 不区分大小写的文件系统（macOS、Windows 默认）上新旧路径是同一个目录
    old = make_folder((tmp_path / "Author").resolve())

    user_path = migrate_user_folder(old, old.parent / "author")

    assert user_path == old.parent / "author"
    assert os.listdir(tmp_path) == ["author"]
    assert (user_path / "video.mp4").is_file()


def test_rename_failure_keeps_using_old_folder(tmp_path, caplog, monkeypatch):
    old = make_folder((tmp_path / "old_name").resolve())

    def deny(self, target):
        raise PermissionError("folder in use")

    monkeypatch.setattr(Path, "rename", deny)
    with caplog.at_level(logging.INFO):
        user_path = migrate_user_folder(old, old.parent / "new_name")

    # 本次继续下载到旧目录，避免在新目录里重新下载一遍，下次运行再尝试重命名
    assert user_path == old
    assert os.listdir(tmp_path) == ["old_name"]
    warnings = f2_messages(caplog, logging.WARNING)
    assert len(warnings) == 1 and "folder in use" in warnings[0]


@pytest.mark.parametrize("old_name", ["..", ".", "a/b"])
def test_unusual_old_name_moves_nothing(tmp_path, old_name):
    parent = (tmp_path / "Download" / "douyin" / "post").resolve()
    make_folder(parent / "a" / "b")

    user_path = migrate_user_folder((parent / old_name).resolve(), parent / "new_name")

    assert user_path == parent / "new_name"
    assert sorted(os.listdir(parent)) == ["a"]
    assert (parent / "a" / "b" / "video.mp4").is_file()


def test_brackets_in_path_are_logged_as_text(tmp_path, caplog):
    # 控制台日志开启了 rich 标记，路径里的 "[/...]" 不能被当成结束标记而抛出异常
    parent = (tmp_path / "x[").resolve()
    old = make_folder(parent / "old]")

    with caplog.at_level(logging.INFO):
        user_path = migrate_user_folder(old, parent / "new]")

    assert (user_path / "video.mp4").is_file()
    assert any(str(old) in m for m in f2_messages(caplog, logging.INFO))


async def test_tiktok_finds_record_by_secuid_after_unique_id_change(
    tmp_path, monkeypatch
):
    # 单个作品与直播模式只知道新的 uniqueId，按它查不到旧记录时要再按 secUid 查
    kwargs = {
        "headers": {"User-Agent": "f2-test", "Referer": "https://example.com/"},
        "cookie": "a=b",
        "proxies": {"http://": None, "https://": None},
        "path": str(tmp_path / "Download"),
        "mode": "one",
    }
    old = make_folder(user_folder(tmp_path, "tiktok", "old.handle", mode="one"))

    handler = tiktok_handler.TiktokHandler(kwargs)
    profile = SimpleNamespace(
        secUid="sec-uid",
        uniqueId="new_handle",
        _to_dict=lambda: {"secUid": "sec-uid", "uniqueId": "new_handle"},
    )

    async def fetch_user_profile(secUid="", uniqueId=""):
        return profile

    monkeypatch.setattr(handler, "fetch_user_profile", fetch_user_profile)

    async with TiktokUserDB(str(tmp_path / "tiktok_users.db")) as db:
        await db.add_user_info(
            secUid="sec-uid", uniqueId="old.handle", last_aweme_id="123"
        )
        user_path = await handler.get_or_add_user_data(
            secUid="", uniqueId="new_handle", db=db
        )
        record = await db.get_user_info(secUid="sec-uid")

    assert user_path == user_folder(tmp_path, "tiktok", "new_handle", mode="one")
    assert (user_path / "video.mp4").is_file()
    assert not old.exists()
    # 旧记录没有被当成新用户整行覆盖
    assert record["last_aweme_id"] == "123"
