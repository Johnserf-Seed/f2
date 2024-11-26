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
    APIFilterError,
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
from .conf_exceptions import ConfError, InvalidEncodingError


__all__ = [
    "APIError",
    "APIConnectionError",
    "APIUnavailableError",
    "APITimeoutError",
    "APIUnauthorizedError",
    "APINotFoundError",
    "APIRateLimitError",
    "APIResponseError",
    "APIFilterError",
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
    "ConfError",
    "InvalidEncodingError",
]
