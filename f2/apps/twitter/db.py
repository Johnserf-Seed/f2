# path: f2/apps/twitter/db.py

from f2.db.base_db import BaseDB


class AsyncUserDB(BaseDB):
    TABLE_NAME = "user_info_web"

    async def _create_table(self) -> None:
        """
        在数据库中创建用户信息表
        """
        await super()._create_table()

        fields = [
            "user_id TEXT",
            "user_unique_id TEXT PRIMARY KEY",
            "user_rest_id TEXT",
            "join_time TEXT",
            "nickname TEXT",
            "nickname_raw TEXT",
            "user_description TEXT",
            "user_description_raw TEXT",
            "user_pined_tweet_id TEXT",
            "user_profile_banner_url TEXT",
            "followers_count INTEGER",
            "friends_count INTEGER",
            "statuses_count INTEGER",
            "media_count INTEGER",
            "favourites_count INTEGER",
            "has_custom_timelines BOOLEAN",
            "location TEXT",
            "can_dm BOOLEAN",
            "is_blue_verified BOOLEAN",
        ]

        fields_sql = ", ".join(fields)
        await self.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} ({fields_sql})"""
        )
        await self.commit()

    async def add_user_info(self, ignore_fields=None, **kwargs) -> None:
        """
        添加用户信息

        Args:
            ignore_fields: 要忽略的字段列表，例如 ["field1", "field2"]
            **kwargs: 用户的其他字段键值对
        """

        # 如果 ignore_fields 未提供或者为 None，将其设置为空列表
        ignore_fields = ignore_fields or []

        # 从 kwargs 中删除要忽略的字段
        for field in ignore_fields:
            if field in kwargs:
                del kwargs[field]

        keys = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        values = tuple(kwargs.values())

        await self.execute(
            f"INSERT OR REPLACE INTO {self.TABLE_NAME} ({keys}) VALUES ({placeholders})",
            values,
        )
        await self.commit()

    async def update_user_info(self, uniqueId: str, **kwargs) -> None:
        """
        更新用户信息

        Args:
            uniqueId (str): 用户唯一标识
            **kwargs: 用户的其他字段键值对
        """

        user_data = await self.get_user_info(uniqueId)
        if user_data:
            set_sql = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            await self.execute(
                f"UPDATE {self.TABLE_NAME} SET {set_sql} WHERE user_unique_id=?",
                (*kwargs.values(), uniqueId),
            )
            await self.commit()

    async def get_user_info(self, uniqueId: str) -> dict:
        """
        获取用户信息

        Args:
            uniqueId (str): 用户唯一标识

        Returns:
            dict: 对应的用户信息，如果不存在则返回 None
        """
        cursor = await self.execute(
            f"SELECT * FROM {self.TABLE_NAME} WHERE user_unique_id=?", (uniqueId,)
        )
        result = await cursor.fetchone()
        if not result:
            return {}
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))

    async def delete_user_info(self, uniqueId: str) -> None:
        """
        删除用户信息

        Args:
            uniqueId (str): 用户唯一标识
        """
        await self.execute(
            f"DELETE FROM {self.TABLE_NAME} WHERE user_unique_id=?", (uniqueId,)
        )
        await self.commit()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
