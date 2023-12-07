# path: f2/db/base_db.py

import aiosqlite
from typing import Optional


class BaseDB:
    def __init__(self, db_name: str) -> Optional[None]:
        self.db_name = db_name
        self.conn = None

    async def connect(self) -> Optional[None]:
        """
        连接到数据库
        """
        self.conn = await aiosqlite.connect(self.db_name)
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
        执行SQL查询

        Args:
            query (str): SQL查询
            parameters (tuple): SQL参数

        Returns:
            aiosqlite.Cursor: 返回查询的光标
        """
        cursor = await self.conn.cursor()
        if parameters:
            await cursor.execute(query, parameters)
        else:
            await cursor.execute(query)
        return cursor

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
