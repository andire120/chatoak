from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    content: str

class MessageDisplay(BaseModel):
    id: int
    room_id: int
    sender_id: int
    sender_username: str # 메시지 조회 시 유저 이름도 함께
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True