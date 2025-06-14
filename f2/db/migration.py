# path: f2/db/migration.py

from abc import abstractmethod
from typing import Optional

from f2.i18n.translator import _
from f2.log.logger import logger


class MigrationMixin:
    """
    迁移混合类 (Migration Mixin)
    提供数据库表结构迁移功能，允许添加缺失的列而不删除现有数据。
    该类应与具体的数据库类一起使用，提供迁移方法以确保表结构与预期一致。

    类属性:
    - TABLE_NAME (Optional[str]): 数据库表名称，子类应定义此属性。
    - execute: 执行 SQL 查询并返回查询的光标。
    - commit: 提交数据库更改，保存数据。
    - migrate: 迁移数据库表结构，添加缺失的列但不删除现有数据。
    类方法:
    - _table_exists: 检查表是否存在，返回布尔值。
    异常处理:
    - 在迁移过程中，如果添加列失败，将记录错误信息。
    使用示例:
    ```python
        class MyDatabase(MigrationMixin):
            TABLE_NAME = "my_table"

            async def execute(self, query: str, parameters: tuple = ...):
                # 实现具体的执行逻辑
                pass

            async def commit(self) -> None:
                # 实现提交逻辑
                pass

        db = MyDatabase()
        await db.migrate({"new_column": "TEXT"})
    ```
    """

    TABLE_NAME: Optional[str]

    @abstractmethod
    async def execute(self, query: str, parameters: tuple = ...): ...

    @abstractmethod
    async def commit(self) -> None: ...

    async def migrate(self, expected_columns: dict) -> None:
        """迁移数据库表结构，添加缺失的列但不删除现有数据"""
        if not self.TABLE_NAME:
            logger.warning(_("无法迁移表：未定义 TABLE_NAME"))
            return

        if not await self._table_exists():
            return

        cursor = await self.execute(f"PRAGMA table_info({self.TABLE_NAME})")
        existing_columns = {column[1]: column[2] for column in await cursor.fetchall()}

        for column, column_type in expected_columns.items():
            if column not in existing_columns:
                try:
                    await self.execute(
                        f"ALTER TABLE {self.TABLE_NAME} ADD COLUMN {column} {column_type}"
                    )
                    logger.info(
                        _("添加列 {0} 到表 {1}").format(column, self.TABLE_NAME)
                    )
                except Exception as e:
                    logger.error(
                        _("添加列 {0} 到表 {1} 失败: {2}").format(
                            column, self.TABLE_NAME, str(e)
                        )
                    )

        await self.commit()

    async def _table_exists(self) -> bool:
        """检查表是否存在"""
        if not self.TABLE_NAME:
            return False

        cursor = await self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (self.TABLE_NAME,),
        )
        return await cursor.fetchone() is not None
