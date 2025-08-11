from pydantic import BaseModel
from datetime import datetime

class RoomCreate(BaseModel):
    name: str

class RoomBase(BaseModel):
    name: str

class RoomDisplay(BaseModel): # <-- 이 부분을 확인해주세요. 이름이 RoomDisplay인지.
    id: int
    name: str
    created_by: int # User ID
    created_at: datetime

    class Config:
        from_attributes = True

class Room(RoomBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        orm_mode = True # SQLAlchemy 모델과 Pydantic 모델을 연결해줍니다.        