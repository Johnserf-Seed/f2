# path: tests/test_user_folder_errors.py

import importlib
import os
import sys

import pytest

from f2.exceptions import ConfError

APPS = ["douyin", "tiktok", "twitter", "weibo"]


@pytest.mark.parametrize("app", APPS)
def test_path_pointing_to_a_file_is_a_config_error(tmp_path, app):
    # 此前 --path 指向已有的文件时 mkdir 抛出 NotADirectoryError，命令行打印完整堆栈
    utils = importlib.import_module(f"f2.apps.{app}.utils")
    afile = tmp_path / "afile.txt"
    afile.write_text("x", encoding="utf-8")

    with pytest.raises(ConfError, match="afile.txt"):
        utils.create_user_folder({"path": str(afile), "mode": "post"}, "user")


@pytest.mark.skipif(
    sys.platform == "win32" or os.geteuid() == 0,
    reason="Windows 与 root 用户不受目录权限限制",
)
def test_read_only_path_is_a_config_error(tmp_path):
    utils = importlib.import_module("f2.apps.douyin.utils")
    readonly = tmp_path / "readonly"
    readonly.mkdir()
    readonly.chmod(0o500)
    try:
        with pytest.raises(ConfError, match="readonly"):
            utils.create_user_folder({"path": str(readonly), "mode": "post"}, "user")
    finally:
        readonly.chmod(0o700)


def test_user_folder_is_created(tmp_path):
    utils = importlib.import_module("f2.apps.douyin.utils")

    path = utils.create_user_folder({"path": str(tmp_path), "mode": "post"}, "user")

    assert path == (tmp_path / "douyin" / "post" / "user").resolve()
    assert path.is_dir()
