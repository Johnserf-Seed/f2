# path: f2/apps/douyin/db.py

from f2.db.base_db import BaseDB


class AsyncUserDB(BaseDB):
    TABLE_NAME = "user_info_web"

    async def _create_table(self) -> None:
        """
        在数据库中创建用户信息表
        """
        await super()._create_table()

        fields = [
            "sec_user_id TEXT PRIMARY KEY",
            "avatar_url TEXT",
            "aweme_count INTEGER",
            "city TEXT",
            "country TEXT",
            "favoriting_count INTEGER",
            "follower_count INTEGER",
            "following_count INTEGER",
            "gender INTEGER",
            "ip_location TEXT",
            "is_ban BOOLEAN",
            "is_block BOOLEAN",
            "is_blocked BOOLEAN",
            "is_star BOOLEAN",
            "live_status INTEGER",
            "mix_count INTEGER",
            "mplatform_followers_count INTEGER",
            "nickname TEXT",
            "nickname_raw TEXT",
            "room_id TEXT",
            "school_name TEXT",
            "short_id TEXT",
            "signature TEXT",
            "signature_raw TEXT",
            "total_favorited INTEGER",
            "uid TEXT",
            "unique_id TEXT",
            "user_age INTEGER",
            "last_aweme_id TEXT",
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
        # VALUES (?, {placeholders})', (kwargs.get('sec_user_id'), *values))
        await self.commit()

    async def update_user_info(self, sec_user_id: str, **kwargs) -> None:
        """
        更新用户信息

        Args:
            sec_user_id (str): 用户唯一标识
            **kwargs: 用户的其他字段键值对
        """

        user_data = await self.get_user_info(sec_user_id)
        if user_data:
            set_sql = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            await self.execute(
                f"UPDATE {self.TABLE_NAME} SET {set_sql} WHERE sec_user_id=?",
                (*kwargs.values(), sec_user_id),
            )
            await self.commit()

    async def get_user_info(self, sec_user_id: str) -> dict:
        """
        获取用户信息

        Args:
            sec_user_id (str): 用户唯一标识

        Returns:
            dict: 对应的用户信息，如果不存在则返回 None
        """
        cursor = await self.execute(
            f"SELECT * FROM {self.TABLE_NAME} WHERE sec_user_id=?", (sec_user_id,)
        )
        result = await cursor.fetchone()
        if not result:
            return {}
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))

    async def delete_user_info(self, sec_user_id: str) -> None:
        """
        删除用户信息

        Args:
            sec_user_id (str): 用户唯一标识
        """
        await self.execute(
            f"DELETE FROM {self.TABLE_NAME} WHERE sec_user_id=?", (sec_user_id,)
        )
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
        fields = [
            "api_status_code TEXT",
            "aweme_id TEXT PRIMARY KEY",
            "aweme_type TEXT",
            "nickname TEXT",
            "nickname_raw TEXT",
            "sec_user_id TEXT",
            "short_id TEXT",
            "uid TEXT",
            "unique_id TEXT",
            "can_comment TEXT",
            "can_forward TEXT",
            "can_share TEXT",
            "can_show_comment TEXT",
            "comment_gid TEXT",
            "create_time TEXT",
            "desc TEXT",
            "desc_raw TEXT",
            "duration TEXT",
            "is_ads TEXT",
            "is_story TEXT",
            "is_top TEXT",
            "video_bit_rate JSON",
            "video_play_addr TEXT",
            "images JSON",
            "animated_cover TEXT",
            "cover TEXT",
            "part_see TEXT",
            "private_status TEXT",
            "is_delete TEXT",
            "is_prohibited TEXT",
            "is_long_video TEXT",
            "media_type TEXT",
            "mix_desc TEXT",
            "mix_desc_raw TEXT",
            "mix_create_time TEXT",
            "mix_id TEXT",
            "mix_name TEXT",
            "mix_pic_type TEXT",
            "mix_type TEXT",
            "mix_share_url TEXT",
            "mix_update_time TEXT",
            "is_commerce_music TEXT",
            "is_original TEXT",
            "is_original_sound TEXT",
            "is_pgc TEXT",
            "music_author TEXT",
            "music_author_raw TEXT",
            "music_author_deleted TEXT",
            "music_duration TEXT",
            "music_id TEXT",
            "music_mid TEXT",
            "pgc_author TEXT",
            "pgc_author_raw TEXT",
            "pgc_author_title TEXT",
            "pgc_author_title_raw TEXT",
            "pgc_music_type TEXT",
            "music_status TEXT",
            "music_owner_handle TEXT",
            "music_owner_handle_raw TEXT",
            "music_owner_id TEXT",
            "music_owner_nickname TEXT",
            "music_owner_nickname_raw TEXT",
            "music_play_url TEXT",
            "position TEXT",
            "region TEXT",
            "seo_ocr_content TEXT",
            "allow_douplus TEXT",
            "download_setting TEXT",
            "allow_share TEXT",
            "admire_count TEXT",
            "collect_count TEXT",
            "comment_count TEXT",
            "digg_count TEXT",
            "share_count TEXT",
            "hashtag_ids JSON",
            "hashtag_names JSON",
        ]

        fields_sql = ", ".join(fields)
        await self.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} ({fields_sql})"""
        )
        await self.commit()

    async def add_video_info(self, ignore_fields=None, **kwargs) -> None:
        """
        添加视频信息

        Args:
            ignore_fields: 要忽略的字段列表，例如 ["field1", "field2"]
            **kwargs: 字段键值对, 例如: aweme_id="some_value", desc="some_desc"
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

    async def batch_insert_videos(
        self, video_data_list: list, ignore_fields=None
    ) -> None:
        """
        批量添加视频信息

        Args:
            video_data_list (list): 视频信息列表
            ignore_fields (list): 要忽略的字段列表，例如 ["field1", "field2"]
        """
        # 如果 ignore_fields 未提供或者为 None，将其设置为空列表
        ignore_fields = ignore_fields or []

        # 删除要忽略的字段
        for field in ignore_fields:
            for video_data in video_data_list:
                if field in video_data:
                    del video_data[field]

        keys = ", ".join(video_data_list[0].keys())
        placeholders = ", ".join(["?" for _ in range(len(video_data_list[0]))])

        # 构建插入数据的元组列表
        values = [tuple(video_data.values()) for video_data in video_data_list]

        await self.execute(
            f"INSERT OR REPLACE INTO {self.TABLE_NAME} ({keys}) VALUES ({placeholders})",
            values,
        )
        await self.commit()

    async def get_video_info(self, aweme_id: str) -> dict:
        """
        获取特定视频的信息

        Args:
            aweme_id (str): 视频ID

        Returns:
            dict: 对应视频的信息
        """
        cursor = await self.execute(
            f"SELECT * FROM {self.TABLE_NAME} WHERE aweme_id=?", (aweme_id,)
        )
        result = await cursor.fetchone()

        if not result:
            return {}

        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, result))

    async def update_video_info(self, aweme_id: str, **kwargs) -> None:
        """
        更新视频信息

        Args:
            aweme_id (str): 视频ID
            **kwargs: 要更新的字段键值对
        """
        set_sql = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = tuple(kwargs.values()) + (aweme_id,)

        await self.execute(
            f"UPDATE {self.TABLE_NAME} SET {set_sql} WHERE aweme_id=?", values
        )
        await self.commit()

    async def delete_video_info(self, aweme_id: str) -> None:
        """
        删除特定视频的信息

        Args:
            aweme_id (str): 视频ID
        """
        await self.execute(
            f"DELETE FROM {self.TABLE_NAME} WHERE aweme_id=?", (aweme_id,)
        )
        await self.commit()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
