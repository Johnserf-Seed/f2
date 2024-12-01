# path: f2/apps/weibo/model.py

from typing import Any
from pydantic import BaseModel


# Model
class UserInfo(BaseModel):
    uid: str


class UserInfoByScreenName(BaseModel):
    screen_name: str


class UserDetail(BaseModel):
    uid: str


class UserWeibo(BaseModel):
    uid: str
    page: int = 1
    feature: int = 0
    since_id: str = ""


class WeiboDetail(BaseModel):
    id: str  # like `O8DM0BLLm` or `5020595169001740`
    locale: str = "zh-CN"
