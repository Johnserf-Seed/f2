# path: f2/apps/tiktok/db.py

from f2.db.base_db import BaseDB


class AsyncUserDB(BaseDB):
    TABLE_NAME = "user_info_web"

    async def _create_table(self) -> None:
        """
        在数据库中创建用户信息表
        """
        await super()._create_table()

        fields = [
            "secUid TEXT PRIMARY KEY",
            "avatar_url TEXT",
            "diggCount INTEGER",
            "followerCount INTEGER",
            "followingCount INTEGER",
            "friendCount INTEGER",
            "heartCount INTEGER",
            "videoCount INTEGER",
            "uid TEXT",
            "nickname TEXT",
            "nickname_raw TEXT",
            "uniqueId TEXT",
            "commentSetting BOOLEAN",
            "followingVisibility BOOLEAN",
            "openFavorite BOOLEAN",
            "privateAccount BOOLEAN",
            "showPlayListTab BOOLEAN",
            "relation BOOLEAN",
            "signature TEXT",
            "signature_raw TEXT",
            "ttSeller BOOLEAN",
            "verified BOOLEAN",
            "last_aweme_id TEXT",
            "api_status_code TEXT",
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

    async def update_user_info(self, secUid, **kwargs) -> None:
        """
        更新用户信息

        Args:
            secUid (str): 用户唯一标识
            **kwargs: 用户的其他字段键值对
        """
        user_data = await self.get_user_info(secUid)
        if user_data:
            set_sql = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            await self.execute(
                f"UPDATE {self.TABLE_NAME} SET {set_sql} WHERE secUid=?",
                (*kwargs.values(), secUid),
            )
            await self.commit()

    async def get_user_info(self, secUid: str = "", uniqueId: str = "") -> dict:
        """
        获取用户信息

        Args:
            secUid (str): 用户唯一标识
            uniqueId (str): 用户名

        Returns:
            dict: 对应的用户信息，如果不存在则返回 None
        """
        if secUid:
            cursor = await self.execute(
                f"SELECT * FROM {self.TABLE_NAME} WHERE secUid=?", (secUid,)
            )
        elif uniqueId:
            cursor = await self.execute(
                f"SELECT * FROM {self.TABLE_NAME} WHERE uniqueId=?", (uniqueId,)
            )
        result = await cursor.fetchone()
        if not result:
            return {}
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))

    async def delete_user_info(self, secUid: str) -> None:
        """
        删除用户信息

        Args:
            secUid (str): 用户唯一标识
        """
        await self.execute(f"DELETE FROM {self.TABLE_NAME} WHERE secUid=?", (secUid,))
        await self.commit()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class AsyncVideoDB(BaseDB):
    TABLE_NAME = "video_info"

    async def _create_table(self) -> None:
        """
        在数据库中创建视频信息表
        """
        await super()._create_table()
        pass

    async def add_video_info(self, ignore_fields=None, **kwargs) -> None:
        """
        添加视频信息

        Args:
            ignore_fields: 要忽略的字段列表，例如 ["field1", "field2"]
            **kwargs: 字段键值对, 例如: aweme_id="some_value", desc="some_desc"
        """
        pass

    async def batch_insert_videos(
        self, video_data_list: list, ignore_fields=None
    ) -> None:
        """
        批量添加视频信息

        Args:
            video_data_list (list): 视频信息列表
            ignore_fields (list): 要忽略的字段列表，例如 ["field1", "field2"]
        """
        pass

    async def get_video_info(self, aweme_id: str) -> dict:
        """
        获取特定视频的信息

        Args:
            aweme_id (str): 视频ID

        Returns:
            dict: 对应视频的信息
        """
        return {}

    async def update_video_info(self, aweme_id: str, **kwargs) -> None:
        """
        更新视频信息

        Args:
            aweme_id (str): 视频ID
            **kwargs: 要更新的字段键值对
        """
        pass

    async def delete_video_info(self, aweme_id: str) -> None:
        """
        删除特定视频的信息

        Args:
            aweme_id (str): 视频ID
        """
        pass

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
