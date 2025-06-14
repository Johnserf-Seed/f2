# path: f2/db/migration.py

from f2.i18n.translator import _
from f2.log.logger import logger


class MigrationMixin:
    """Mixin for handling SQLite table migrations."""

    TABLE_NAME: str

    async def execute(self, query: str, parameters: tuple = ...): ...

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
