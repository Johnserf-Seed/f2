# path: f2/exceptions/__init__.py

from .api_exceptions import (
    APIError,
    APIConnectionError,
    APIUnavailableError,
    APINotFoundError,
    APITimeoutError,
    APIUnauthorizedError,
    APIRateLimitError,
    APIResponseError,
    APIRetryExhaustedError,
)
from .db_exceptions import (
    DatabaseConnectionError,
    RecordNotFoundError,
    DatabaseError,
    DatabaseTimeoutError,
    DatabaseConstraintError,
    MultipleRecordsFoundError,
)
from .file_exceptions import (
    FileError,
    FileReadError,
    FileNotFound,
    FilePermissionError,
    FileWriteError,
)


__all__ = [
    "APIError",
    "APIConnectionError",
    "APIUnavailableError",
    "APITimeoutError",
    "APIUnauthorizedError",
    "APINotFoundError",
    "APIRateLimitError",
    "APIResponseError",
    "APIRetryExhaustedError",
    "DatabaseConnectionError",
    "RecordNotFoundError",
    "DatabaseError",
    "DatabaseTimeoutError",
    "DatabaseConstraintError",
    "MultipleRecordsFoundError",
    "FileError",
    "FileReadError",
    "FileNotFound",
    "FilePermissionError",
    "FileWriteError",
]
