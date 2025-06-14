# path: f2/db/base_db.py

import asyncio
from typing import Any, List, Optional, Tuple

import aiosqlite
from aiosqlite import Connection

from f2.db.migration import MigrationMixin
from f2.exceptions.db_exceptions import DatabaseConnectionError, DatabaseTimeoutError
from f2.i18n.translator import _
from f2.log.logger import logger


class BaseDB(MigrationMixin):
    """
    基础数据库类 (Base Database)

    该类提供了一个异步数据库连接管理器，封装了与 SQLite 数据库的连接、查询、数据操作及版本控制等功能。
    支持高并发任务限制、自动重试机制和数据库版本迁移。

    类属性:
    - db_name (str): 数据库名称。
    - conn (aiosqlite.Connection | None): 数据库连接实例，初始化时为 None。
    - semaphore (asyncio.Semaphore): 用于限制并发任务数的信号量。
    - max_retries (int): 最大重试次数，用于处理数据库锁定问题。
    - TABLE_NAME (str | None): 表名称，默认值为 None，由子类覆盖。

    类方法:
    - __init__: 初始化数据库连接管理器，并设置数据库名称。
    - connect: 连接到指定的 SQLite 数据库，并创建表（如果不存在）。
    - _create_table: 在数据库中创建 `_metadata` 表，用于存储元数据，如版本信息。
    - get_version: 获取数据库的当前版本号。如果没有设置版本，返回 0。
    - set_version: 设置数据库的版本号，若该版本已存在则更新。
    - execute: 执行 SQL 查询并返回查询的光标。可以接收查询参数。
    - fetch_one: 执行 SQL 查询并返回一个结果。
    - fetch_all: 执行 SQL 查询并返回所有结果。
    - commit: 提交数据库更改，保存数据。
    - close: 关闭与数据库的连接。
    - migrate: 提供数据库迁移的基础接口，子类可以实现特定的迁移策略。

    异常处理:
    - 该类在连接数据库、执行 SQL 查询及提交更改时，会捕获并处理可能的异常（如连接失败、查询错误等），确保系统稳定运行。

    使用示例:
    ```python
        # 创建 BaseDB 实例并连接数据库
        db = BaseDB("example.db")
        await db.connect()

        # 设置数据库版本
        await db.set_version(1)

        # 获取数据库版本
        version = await db.get_version()

        # 执行查询
        result = await db.fetch_all("SELECT * FROM some_table")

        # 提交更改
        await db.commit()

        # 关闭连接
        await db.close()
    ```
    """

    TABLE_NAME: Optional[str] = None  # 添加默认 TABLE_NAME 属性，由子类覆盖

    def __init__(self, db_name: str, **kwargs) -> None:
        self.db_name = db_name
        self.conn: Optional[Connection] = None
        self.semaphore = asyncio.Semaphore(kwargs.get("max_tasks", 10))
        self.max_retries = kwargs.get("max_retries", 5)

    async def connect(self) -> None:
        """
        连接到数据库并自动迁移表结构

        - 启用 WAL 模式，提高并发读写性能。
        - 设置 `synchronous` 为 `NORMAL`，降低同步写操作的延迟。
        - 增加缓存大小，提高查询速度。
        - 将临时表存储在内存中，加快查询速度。
        """
        try:
            self.conn = await aiosqlite.connect(self.db_name)
            if self.conn is not None:
                await self.conn.execute("PRAGMA journal_mode=WAL;")  # 启用 WAL 模式
                await self.conn.execute(
                    "PRAGMA synchronous = NORMAL;"
                )  # 优化性，,减少同步开销
                await self.conn.execute("PRAGMA cache_size = 10000;")  # 增加缓存大小
                await self.conn.execute(
                    "PRAGMA temp_store = MEMORY;"
                )  # 临时表存储在内存中
                # await self.conn.execute("PRAGMA locking_mode = EXCLUSIVE;")  # 限制数据库独占锁模式
                await self._create_table()

                # 连接后自动执行迁移
                if hasattr(self, "get_table_schema") and self.TABLE_NAME:
                    schema = self.get_table_schema()
                    await self.migrate(schema)
        except aiosqlite.OperationalError as e:
            # 捕获数据库连接错误并抛出自定义异常
            raise DatabaseConnectionError(
                _("数据库连接失败，请检查数据库路径或权限: {0}").format(self.db_name),
            ) from e
        except aiosqlite.DatabaseError as e:
            # 捕获数据库错误并抛出自定义异常
            raise DatabaseTimeoutError(
                _("数据库操作超时: {0}").format(self.db_name)
            ) from e

    async def _create_table(self) -> None:
        """
        在数据库中创建表
        """
        await self.execute(
            """CREATE TABLE IF NOT EXISTS _metadata
                    (name TEXT PRIMARY KEY, value TEXT)"""
        )
        await self.commit()

    async def get_version(self) -> int:
        result = await self.fetch_one(
            'SELECT value FROM _metadata WHERE name="version"'
        )
        return int(result[0]) if result else 0

    async def set_version(self, version: int) -> None:
        await self.execute(
            "INSERT OR REPLACE INTO _metadata (name, value) VALUES (?, ?)",
            ("version", str(version)),
        )
        await self.commit()

    async def execute(
        self, query: str, parameters: Tuple[Any, ...] = ()
    ) -> aiosqlite.Cursor:
        """
        执行SQL查询，并增加重试机制以处理潜在的锁定问题。

        - 支持异步任务的信号量控制，限制最大并发查询数。
        - 在发生 `OperationalError` 时自动重试，最多重试 `max_retries` 次。

        Args:
            query (str): SQL查询
            parameters (tuple): SQL参数

        Returns:
            aiosqlite.Cursor: 查询的光标
        """
        if self.conn is None:
            raise DatabaseConnectionError(_("数据库未连接"))

        for attempt in range(self.max_retries):
            try:
                cursor = await self.conn.cursor()
                async with self.semaphore:
                    if parameters:
                        await cursor.execute(query, parameters)
                    else:
                        await cursor.execute(query)
                return cursor
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < self.max_retries - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))  # 指数级退避
                else:
                    raise
        # 如果所有尝试都失败，抛出异常
        raise DatabaseTimeoutError(_("SQL 执行失败，已重试多次：{0}").format(query))

    async def executemany(
        self, query: str, parameters_sequence: List[Tuple[Any, ...]]
    ) -> None:
        """
        批量执行SQL查询，每条记录使用不同的参数。

        适用于批量插入或更新多行数据。

        Args:
            query (str): SQL查询语句
            parameters_sequence (List[Tuple[Any, ...]]): 参数列表，每个元素是一个元组
        """
        if self.conn is None:
            raise DatabaseConnectionError(_("数据库未连接"))

        for attempt in range(self.max_retries):
            try:
                async with self.semaphore:
                    await self.conn.executemany(query, parameters_sequence)
                return
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < self.max_retries - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))  # 指数级退避
                else:
                    raise
        # 如果所有尝试都失败，抛出异常
        raise DatabaseTimeoutError(_("批量SQL执行失败，已重试多次：{0}").format(query))

    async def fetch_one(
        self, query: str, parameters: Tuple[Any, ...] = ()
    ) -> Optional[Tuple[Any, ...]]:
        """
        执行SQL查询并返回一个结果

        Args:
            query (str): SQL查询
            parameters (tuple): SQL参数

        Returns:
            tuple: 查询的结果
        """
        cursor = await self.execute(query, parameters)
        row = await cursor.fetchone()
        return tuple(row) if row else None

    async def fetch_all(self, query: str, parameters: tuple = ()) -> list:
        """
        执行SQL查询并返回所有结果

        Args:
            query (str): SQL查询
            parameters (tuple): SQL参数

        Returns:
            list: 查询的结果
        """
        cursor = await self.execute(query, parameters)
        rows = await cursor.fetchall()
        return [tuple(row) for row in rows]

    async def commit(self) -> None:
        """
        提交更改到数据库
        """
        if self.conn is not None:
            await self.conn.commit()

    async def close(self) -> None:
        """
        关闭与数据库的连接
        """
        if self.conn:
            await self.conn.close()
