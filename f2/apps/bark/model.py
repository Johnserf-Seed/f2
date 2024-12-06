# path:f2/apps/bark/model.py

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# Base Model
class BarkModel(BaseModel):
    title: Optional[str]
    body: str
    sound: Optional[str]
    call: Optional[int]
    isArchive: Optional[int]
    icon: Optional[str]
    group: Optional[str]
    # ciphertext: Optional[str] = ""
    level: Optional[Literal["active", "timeSensitive", "passive", "critical"]]
    volume: Optional[int]
    url: Optional[str]
    copy_text: Optional[str] = Field(
        "", alias="copy"
    )  # 'copy' 使用别名 'copy_text'，原因是关键词冲突
    badge: Optional[int]
    autoCopy: Optional[int]

    model_config = ConfigDict(populate_by_name=True)
