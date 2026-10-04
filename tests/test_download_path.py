# path: tests/test_download_path.py

from pathlib import Path

import pytest

from f2.utils.file.path import get_user_folder_path


@pytest.fixture
def home(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    return tmp_path


def test_download_path_expands_home(home, tmp_path, monkeypatch):
    # 此前 path: ~/Downloads 会在当前目录下建出名为 ~ 的目录
    monkeypatch.chdir(tmp_path)
    kwargs = {"path": "~/Downloads", "mode": "post"}

    folder = get_user_folder_path(kwargs, "douyin", "alice")

    assert folder == (home / "Downloads" / "douyin" / "post" / "alice").resolve()
    assert "~" not in Path(folder).parts
