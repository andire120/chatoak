from pydantic import BaseModel
from datetime import datetime

class RoomCreate(BaseModel):
    name: str

class RoomDisplay(BaseModel): # <-- 이 부분을 확인해주세요. 이름이 RoomDisplay인지.
    id: int
    name: str
    created_by: int # User ID
    created_at: datetime

    class Config:
        from_attributes = True