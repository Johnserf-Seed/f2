# path: f2/exceptions/__init__.py

from .api_exceptions import (
    APIConnectionError,
    APIError,
    APIFilterError,
    APINotFoundError,
    APIRateLimitError,
    APIResponseError,
    APIRetryExhaustedError,
    APITimeoutError,
    APIUnauthorizedError,
    APIUnavailableError,
)
from .conf_exceptions import ConfError, InvalidEncodingError
from .db_exceptions import (
    DatabaseConnectionError,
    DatabaseConstraintError,
    DatabaseError,
    DatabaseTimeoutError,
    MultipleRecordsFoundError,
    RecordNotFoundError,
)
from .file_exceptions import (
    FileError,
    FileNotFound,
    FilePermissionError,
    FileReadError,
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
