# path: f2/apps/weibo/db.py

from f2.db.base_db import BaseDB


class AsyncUserDB(BaseDB):
    TABLE_NAME = "user_info_web"

    async def _create_table(self) -> None:
        """在数据库中创建用户信息表"""
        await super()._create_table()

        fields = [
            "uid TEXT PRIMARY KEY",
            "nickname TEXT",
            "blockText TEXT",
            "avatar_hd TEXT",
            "cover_image TEXT",
            "description TEXT",
            "follow_me BOOLEAN",
            "following BOOLEAN",
            "followers_count INTEGER",
            "friends_count INTEGER",
            "weibo_count INTEGER",
            "gender TEXT",
            "weihao TEXT",
            "is_muteuser BOOLEAN",
            "is_star TEXT",
            "location TEXT",
            "profile_url TEXT",
            "user_type TEXT",
            "verified BOOLEAN",
            "vvip INTEGER",
        ]

        fields_sql = ", ".join(fields)
        await self.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} ({fields_sql})"""
        )
        await self.commit()

    async def add_user_info(self, ignore_fields: list = None, **kwargs) -> None:
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

    async def updat_user_info(self, uid: str, **kwargs) -> None:
        """
        更新用户信息

        Args:
            uid: 用户 ID
            **kwargs: 用户的其他字段键值对
        """

        user_data = await self.get_user_info(uid)
        if user_data:
            set_sql = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            await self.execute(
                f"UPDATE {self.TABLE_NAME} SET {set_sql} WHERE uid=?",
                (*kwargs.values(), uid),
            )
            await self.commit()

    async def get_user_info(self, uid: str) -> dict:
        """
        获取用户信息

        Args:
            uid: 用户 ID

        Returns:
            dict: 对应的用户信息，如果不存在则返回 None
        """

        cursor = await self.execute(
            f"SELECT * FROM {self.TABLE_NAME} WHERE uid=?", (uid,)
        )
        result = await cursor.fetchone()
        if not result:
            return {}
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))

    async def delete_user_info(self, uid: str) -> None:
        """
        删除用户信息

        Args:
            uid: 用户 ID
        """

        await self.execute(f"DELETE FROM {self.TABLE_NAME} WHERE uid=?", (uid,))
        await self.commit()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
