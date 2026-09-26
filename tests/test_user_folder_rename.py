# path: tests/test_user_folder_rename.py

import logging
import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from f2.apps.douyin import handler as douyin_handler
from f2.apps.douyin import utils as douyin_utils
from f2.apps.douyin.db import AsyncUserDB as DouyinUserDB
from f2.apps.tiktok import handler as tiktok_handler
from f2.apps.tiktok import utils as tiktok_utils
from f2.apps.tiktok.db import AsyncUserDB as TiktokUserDB
from f2.apps.twitter import handler as twitter_handler
from f2.apps.twitter import utils as twitter_utils
from f2.apps.twitter.db import AsyncUserDB as TwitterUserDB
from f2.apps.weibo import handler as weibo_handler
from f2.apps.weibo import utils as weibo_utils
from f2.apps.weibo.db import AsyncUserDB as WeiboUserDB
from f2.utils.file.path import is_user_folder_migrated, migrate_user_folder
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

HANDLER_KWARGS = {
    "headers": {"User-Agent": "f2-test", "Referer": "https://example.com/"},
    "cookie": "a=b",
    "proxies": {"http://": None, "https://": None},
}

# 各应用 handler 的差异：数据库、获取用户资料的方法、记录主键与调用方式
HANDLERS = {
    "douyin": SimpleNamespace(
        handler=douyin_handler.DouyinHandler,
        db=DouyinUserDB,
        fetch="fetch_user_profile",
        record={"sec_user_id": "user-id"},
        key="nickname",
        get_or_add=lambda handler, db: handler.get_or_add_user_data(
            handler.kwargs, "user-id", db
        ),
        read=lambda db: db.get_user_info("user-id"),
    ),
    "tiktok": SimpleNamespace(
        handler=tiktok_handler.TiktokHandler,
        db=TiktokUserDB,
        fetch="fetch_user_profile",
        record={"secUid": "user-id"},
        key="uniqueId",
        get_or_add=lambda handler, db: handler.get_or_add_user_data(
            secUid="user-id", uniqueId="", db=db
        ),
        read=lambda db: db.get_user_info(secUid="user-id"),
    ),
    "twitter": SimpleNamespace(
        handler=twitter_handler.TwitterHandler,
        db=TwitterUserDB,
        fetch="fetch_user_profile",
        record={"user_unique_id": "user-id"},
        key="nickname",
        get_or_add=lambda handler, db: handler.get_or_add_user_data(
            handler.kwargs, "user-id", db
        ),
        read=lambda db: db.get_user_info("user-id"),
    ),
    "weibo": SimpleNamespace(
        handler=weibo_handler.WeiboHandler,
        db=WeiboUserDB,
        fetch="fetch_user_info",
        record={"uid": "user-id"},
        key="nickname",
        get_or_add=lambda handler, db: handler.get_or_add_user_data(
            handler.kwargs, "user-id", db
        ),
        read=lambda db: db.get_user_info("user-id"),
    ),
}


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


def make_handler(tmp_path, monkeypatch, app, profile):
    """构造 handler，获取用户资料时返回 profile，不发起请求"""
    case = HANDLERS[app]
    handler = case.handler(
        dict(HANDLER_KWARGS, path=str(tmp_path / "Download"), mode="post")
    )

    async def fetch(*args, **kwargs):
        return profile

    monkeypatch.setattr(handler, case.fetch, fetch)
    return handler


def profile_named(name):
    # 各应用 handler 只读取自己需要的字段：昵称或 uniqueId
    return SimpleNamespace(
        nickname=name, nickname_raw=name, uniqueId=name, secUid="user-id", _to_dict=dict
    )


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
    # 本地记录还没更新时会再比较一次，不能反复提示或改动目录
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
def test_renames_folders_in_every_mode(tmp_path, kwargs, app, utils, key):
    # 同一用户在各下载模式下的目录一起改名，以后用其他模式下载时不会另建目录
    modes = ("post", "like", "one")
    for mode in modes:
        make_folder(
            user_folder(tmp_path, app, "old_name", mode=mode), files=(f"{mode}.mp4",)
        )

    user_path = utils.create_or_rename_user_folder(
        kwargs, {key: "old_name"}, "new_name"
    )

    assert user_path == user_folder(tmp_path, app, "new_name")
    for mode in modes:
        folder = user_folder(tmp_path, app, "new_name", mode=mode)
        assert os.listdir(folder) == [f"{mode}.mp4"]
        assert os.listdir(folder.parent) == ["new_name"]
    assert is_user_folder_migrated(kwargs, app, "old_name", "new_name")


def test_conflict_in_one_mode_does_not_block_other_modes(tmp_path, kwargs, caplog):
    like_old = make_folder(
        user_folder(tmp_path, "douyin", "old_name", mode="like"), files=("old.mp4",)
    )
    make_folder(
        user_folder(tmp_path, "douyin", "new_name", mode="like"), files=("new.mp4",)
    )
    make_folder(user_folder(tmp_path, "douyin", "old_name"))

    with caplog.at_level(logging.INFO):
        user_path = douyin_utils.create_or_rename_user_folder(
            kwargs, {"nickname": "old_name"}, "new_name"
        )

    # 当前模式照常改名；有冲突的模式两个目录都保留并提示
    assert (user_path / "video.mp4").is_file()
    assert sorted(os.listdir(like_old.parent)) == ["new_name", "old_name"]
    assert len(f2_messages(caplog, logging.WARNING)) == 1
    # 还有没改名的旧目录，本地记录先不更新
    assert not is_user_folder_migrated(kwargs, "douyin", "old_name", "new_name")


def test_is_user_folder_migrated(tmp_path, kwargs):
    # 名称没有变化或为空时不需要更新本地记录
    assert not is_user_folder_migrated(kwargs, "douyin", "name", "name")
    assert not is_user_folder_migrated(kwargs, "douyin", None, "name")
    assert not is_user_folder_migrated(kwargs, "douyin", "name", "")
    # 没有任何旧目录时（包括应用目录还不存在）可以直接更新
    assert is_user_folder_migrated(kwargs, "douyin", "old_name", "new_name")

    old = make_folder(user_folder(tmp_path, "douyin", "old_name", mode="like"))
    assert not is_user_folder_migrated(kwargs, "douyin", "old_name", "new_name")

    old.rename(old.parent / "new_name")
    assert is_user_folder_migrated(kwargs, "douyin", "old_name", "new_name")


def test_rename_failure_keeps_record_for_next_run(tmp_path, kwargs, monkeypatch):
    old = make_folder(user_folder(tmp_path, "douyin", "old_name"))

    def deny(self, target):
        raise PermissionError("folder in use")

    monkeypatch.setattr(Path, "rename", deny)
    user_path = douyin_utils.create_or_rename_user_folder(
        kwargs, {"nickname": "old_name"}, "new_name"
    )

    # 本次下载到旧目录，本地记录保留旧名称，下次运行再尝试重命名
    assert user_path == old
    assert not is_user_folder_migrated(kwargs, "douyin", "old_name", "new_name")


def test_case_only_change_is_renamed_once(tmp_path, kwargs, caplog):
    # 不区分大小写的文件系统（macOS、Windows 默认）上 "Author" 与 "author" 是同一个目录
    make_folder(user_folder(tmp_path, "douyin", "Author"))
    douyin_utils.create_or_rename_user_folder(kwargs, {"nickname": "Author"}, "author")

    assert os.listdir(user_folder(tmp_path, "douyin", "author").parent) == ["author"]
    assert is_user_folder_migrated(kwargs, "douyin", "Author", "author")

    caplog.clear()
    with caplog.at_level(logging.INFO):
        douyin_utils.create_or_rename_user_folder(
            kwargs, {"nickname": "Author"}, "author"
        )
    assert f2_messages(caplog, logging.INFO) == []


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


@pytest.mark.parametrize("app", HANDLERS)
async def test_handler_follows_every_rename(tmp_path, monkeypatch, app):
    case = HANDLERS[app]
    profile = profile_named("A")
    handler = make_handler(tmp_path, monkeypatch, app, profile)
    for mode in ("post", "like"):
        make_folder(user_folder(tmp_path, app, "A", mode=mode), files=(f"{mode}.mp4",))

    async with case.db(str(tmp_path / f"{app}_users.db")) as db:
        await db.add_user_info(**case.record, **{case.key: "A"})
        # 先改名为 B、之后又改名为 C：每次都把各模式的目录一起改名并更新本地记录
        for name in ("B", "C"):
            profile.nickname = profile.nickname_raw = profile.uniqueId = name
            user_path = await case.get_or_add(handler, db)
            assert user_path == user_folder(tmp_path, app, name)
            assert (await case.read(db))[case.key] == name

    for mode in ("post", "like"):
        folder = user_folder(tmp_path, app, "C", mode=mode)
        assert os.listdir(folder) == [f"{mode}.mp4"]
        assert os.listdir(folder.parent) == ["C"]


@pytest.mark.parametrize("app", HANDLERS)
async def test_handler_keeps_record_until_conflict_is_resolved(
    tmp_path, monkeypatch, caplog, app
):
    case = HANDLERS[app]
    handler = make_handler(tmp_path, monkeypatch, app, profile_named("B"))
    old = make_folder(user_folder(tmp_path, app, "A"), files=("old.mp4",))
    make_folder(user_folder(tmp_path, app, "B"), files=("new.mp4",))

    async with case.db(str(tmp_path / f"{app}_users.db")) as db:
        await db.add_user_info(**case.record, **{case.key: "A"})

        # 新旧目录同时存在：每次运行都提示，本地记录保留旧名称
        with caplog.at_level(logging.INFO):
            for _ in range(2):
                await case.get_or_add(handler, db)
        assert len(f2_messages(caplog, logging.WARNING)) == 2
        assert (await case.read(db))[case.key] == "A"

        # 手动合并并删除旧目录后不再提示，本地记录更新为新名称
        shutil.rmtree(old)
        caplog.clear()
        with caplog.at_level(logging.INFO):
            await case.get_or_add(handler, db)
        assert f2_messages(caplog, logging.WARNING) == []
        assert (await case.read(db))[case.key] == "B"


async def test_tiktok_finds_record_by_secuid_after_unique_id_change(
    tmp_path, monkeypatch
):
    # 单个作品与直播模式只知道新的 uniqueId，按它查不到旧记录时要再按 secUid 查
    kwargs = dict(HANDLER_KWARGS, path=str(tmp_path / "Download"), mode="one")
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
    # 旧记录没有被当成新用户整行覆盖，只更新了 uniqueId
    assert record["uniqueId"] == "new_handle"
    assert record["last_aweme_id"] == "123"
