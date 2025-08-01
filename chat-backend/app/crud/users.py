# app/crud/users.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User # User 모델 임포트

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: dict): # schemas.UserCreate 등을 사용할 수도 있지만 일단 dict로
    db_user = User(username=user["username"], hashed_password=user["hashed_password"])
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- 회원 탈퇴 함수 추가 ---
async def delete_user(db: AsyncSession, user_id: int):
    """
    주어진 user_id에 해당하는 사용자를 삭제합니다.
    User 모델의 cascade 설정에 따라 관련 ChatRoom 및 Message도 함께 삭제됩니다.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False