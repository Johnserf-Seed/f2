# path: tests/test_db_version.py

import sqlite3

import pytest

from f2.db.base_db import BaseDB


@pytest.mark.skipif(
    not hasattr(sqlite3.Connection, "setconfig"), reason="Python 3.12 起才能关闭 DQS"
)
async def test_version_query_works_without_double_quoted_strings(tmp_path):
    # 此前 WHERE name="version" 依赖 SQLite 把双引号当作字符串，关闭 DQS 时报 no such column
    db = BaseDB(str(tmp_path / "f2.db"))
    await db.connect()
    try:
        conn = db.conn._conn  # aiosqlite 包装的 sqlite3 连接
        await db.conn._execute(conn.setconfig, sqlite3.SQLITE_DBCONFIG_DQS_DML, False)

        await db.set_version(3)
        assert await db.get_version() == 3
    finally:
        await db.close()
