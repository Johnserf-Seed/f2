# path: tests/test_exceptions.py

import pytest

from f2.exceptions import (
    APIConnectionError,
    APIError,
    APIUnavailableError,
    DatabaseConnectionError,
    DatabaseConstraintError,
    DatabaseError,
    DatabaseTimeoutError,
    F2Error,
    FileNotFound,
    MultipleRecordsFoundError,
    RecordNotFoundError,
)


class MockAPI:
    def raise_exception(self, exception_name):
        if exception_name == "APIError":
            raise APIError("APIError occurred")
        elif exception_name == "APIConnectionError":
            raise APIConnectionError("APIConnectionError occurred")
        elif exception_name == "APIUnavailableError":
            raise APIUnavailableError("APIUnavailableError occurred")
        else:
            raise ValueError("Invalid API exception name")


class MockDatabase:
    def raise_exception(self, exception_name):
        if exception_name == "DatabaseConnectionError":
            raise DatabaseConnectionError("DatabaseConnectionError occurred")
        elif exception_name == "RecordNotFoundError":
            raise RecordNotFoundError("RecordNotFoundError occurred")
        elif exception_name == "DatabaseError":
            raise DatabaseError("DatabaseError occurred")
        elif exception_name == "DatabaseTimeoutError":
            raise DatabaseTimeoutError("DatabaseTimeoutError occurred")
        elif exception_name == "DatabaseConstraintError":
            raise DatabaseConstraintError("DatabaseConstraintError occurred")
        elif exception_name == "MultipleRecordsFoundError":
            raise MultipleRecordsFoundError("MultipleRecordsFoundError occurred")
        else:
            raise ValueError("Invalid Database exception name")


def test_api_exceptions():
    api = MockAPI()

    with pytest.raises(APIError):
        api.raise_exception("APIError")

    with pytest.raises(APIConnectionError):
        api.raise_exception("APIConnectionError")

    with pytest.raises(APIUnavailableError):
        api.raise_exception("APIUnavailableError")


def test_db_exceptions():
    db = MockDatabase()

    with pytest.raises(DatabaseConnectionError):
        db.raise_exception("DatabaseConnectionError")

    with pytest.raises(RecordNotFoundError):
        db.raise_exception("RecordNotFoundError")

    with pytest.raises(DatabaseError):
        db.raise_exception("DatabaseError")

    with pytest.raises(DatabaseTimeoutError):
        db.raise_exception("DatabaseTimeoutError")

    with pytest.raises(DatabaseConstraintError):
        db.raise_exception("DatabaseConstraintError")

    with pytest.raises(MultipleRecordsFoundError):
        db.raise_exception("MultipleRecordsFoundError")


def test_all_exception_families_share_the_f2_root():
    from f2.exceptions import APIError, ConfError, DatabaseError, FileError

    for cls in (APIError, ConfError, DatabaseError, FileError):
        assert issubclass(cls, F2Error)
    # 库使用者只捕获 F2Error 即可
    with pytest.raises(F2Error):
        raise APIError("boom", status_code=500)


def test_handler_main_rejects_unknown_mode():
    import asyncio

    from f2.apps.douyin import handler

    with pytest.raises(F2Error):
        asyncio.run(handler.main({"mode": "no-such-mode"}))


def test_file_error_message_is_kept_without_filepath():
    # 没有文件路径时不能返回空字符串，否则 CLI 的"运行中止"只剩一个冒号（#433）
    assert str(FileNotFound("config missing")) == "config missing"
    assert (
        str(FileNotFound("config missing", filepath="/tmp/app.yaml"))
        == "config missing Filepath: /tmp/app.yaml"
    )
