from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str # <-- 반드시 'password: str' 이어야 합니다.

class UserLogin(BaseModel):
    username: str
    password: str # <-- 반드시 'password: str' 이어야 합니다.

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInDB(BaseModel): # 실제 DB 모델을 반영 (비밀번호 해시 포함)
    id: int
    username: str
    password_hash: str # <-- 반드시 'password_hash: str' 이어야 합니다.

    class Config:
        from_attributes = True