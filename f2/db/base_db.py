# path: f2/db/base_db.py

import asyncio
import aiosqlite

from typing import Optional


class BaseDB:
    """
    基础数据库类 (Base Database)

    该类提供了一个异步数据库连接管理器，封装了与 SQLite 数据库的连接、查询、数据操作及版本控制等功能。
    支持高并发任务限制、自动重试机制和数据库版本迁移。

    类属性:
    - db_name (str): 数据库名称。
    - conn (aiosqlite.Connection | None): 数据库连接实例，初始化时为 None。
    - semaphore (asyncio.Semaphore): 用于限制并发任务数的信号量。
    - max_retries (int): 最大重试次数，用于处理数据库锁定问题。

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

    def __init__(self, db_name: str, **kwargs) -> Optional[None]:
        self.db_name = db_name
        self.conn = None
        self.semaphore = asyncio.Semaphore(kwargs.get("max_tasks", 10))
        self.max_retries = kwargs.get("max_retries", 5)

    async def connect(self) -> Optional[None]:
        """
        连接到数据库

        - 启用 WAL 模式，提高并发读写性能。
        - 设置 `synchronous` 为 `NORMAL`，降低同步写操作的延迟。
        - 增加缓存大小，提高查询速度。
        - 将临时表存储在内存中，加快查询速度。
        """
        self.conn = await aiosqlite.connect(self.db_name)
        await self.conn.execute("PRAGMA journal_mode=WAL;")  # 启用 WAL 模式
        await self.conn.execute("PRAGMA synchronous = NORMAL;")  # 优化性，,减少同步开销
        await self.conn.execute("PRAGMA cache_size = 10000;")  # 增加缓存大小
        await self.conn.execute("PRAGMA temp_store = MEMORY;")  # 临时表存储在内存中
        # await self.conn.execute("PRAGMA locking_mode = EXCLUSIVE;")  # 限制数据库独占锁模式
        await self._create_table()

    async def _create_table(self) -> Optional[None]:
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

    async def set_version(self, version: int) -> Optional[None]:
        await self.execute(
            "INSERT OR REPLACE INTO _metadata (name, value) VALUES (?, ?)",
            ("version", str(version)),
        )
        await self.commit()

    async def execute(self, query: str, parameters: tuple = ()) -> aiosqlite.Cursor:
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

    async def fetch_one(self, query: str, parameters: tuple = ()) -> tuple:
        """
        执行SQL查询并返回一个结果

        Args:
            query (str): SQL查询
            parameters (tuple): SQL参数

        Returns:
            tuple: 查询的结果
        """
        cursor = await self.execute(query, parameters)
        return await cursor.fetchone()

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
        return await cursor.fetchall()

    async def commit(self) -> Optional[None]:
        """
        提交更改到数据库
        """
        await self.conn.commit()

    async def close(self) -> Optional[None]:
        """
        关闭与数据库的连接
        """
        if self.conn:
            await self.conn.close()

    async def migrate(self):
        """
        Base migration logic. This should be overridden by subclasses
        to provide specific migration strategies.
        """
        raise NotImplementedError(
            "Migration strategy not implemented for this DB class"
        )
