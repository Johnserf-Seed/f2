# path: tests/test_excetions.py

import pytest

from f2.exceptions import (
    APIConnectionError,
    APIError,
    APIUnavailableError,
    DatabaseConnectionError,
    DatabaseConstraintError,
    DatabaseError,
    DatabaseTimeoutError,
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
