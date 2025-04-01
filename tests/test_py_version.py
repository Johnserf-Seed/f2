# path: tests/test_py_version.py

from unittest.mock import patch

import pytest

from f2.utils.utils import check_python_version


# 测试 Python 版本满足最低要求时不会退出程序
def test_version_meets_requirement():
    with patch("sys.version_info", (3, 10, 0)):
        try:
            check_python_version((3, 10))
        except SystemExit:
            pytest.fail("check_python_version raised SystemExit unexpectedly!")


# 测试 Python 版本低于最低要求时触发 SystemExit
def test_version_below_requirement():
    with patch("sys.version_info", (3, 9, 0)):
        with pytest.raises(SystemExit):
            check_python_version((3, 10))


# 测试 Python 版本高于最低要求时不会退出程序
def test_version_above_requirement():
    with patch("sys.version_info", (3, 11, 0)):
        try:
            check_python_version((3, 10))
        except SystemExit:
            pytest.fail("check_python_version raised SystemExit unexpectedly!")


# 测试 Python 版本精确匹配最低要求时不会退出程序
def test_version_exact_match():
    with patch("sys.version_info", (3, 10, 5)):
        try:
            check_python_version((3, 10))
        except SystemExit:
            pytest.fail("check_python_version raised SystemExit unexpectedly!")
