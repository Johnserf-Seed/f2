# path:f2/apps/bark/model.py

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Base Model
class BarkModel(BaseModel):
    title: Optional[str]
    body: str
    sound: Optional[str] = "birdsong"
    call: Optional[int] = 0
    isArchive: Optional[int] = 1
    icon: Optional[str] = "https://f2.wiki/f2-logo-with-shadow.png"
    group: Optional[str] = "F2下载统计"
    level: Optional[Literal["active", "timeSensitive", "passive", "critical"]] = (
        "active"
    )
    volume: Optional[int] = 5
    url: Optional[str] = "https://f2.wiki/"
    copy_text: Optional[str] = Field(
        "", alias="copy"
    )  # 'copy' 使用别名 'copy_text'，原因是关键词冲突
    badge: Optional[int] = 1
    autoCopy: Optional[int] = 1

    model_config = ConfigDict(populate_by_name=True)


class BarkCipherModel(BaseModel):
    ciphertext: Optional[str]
    iv: Optional[str]
