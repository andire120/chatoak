# app/api/v1/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.crud import users as crud_users
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter()

# 이 파일에 users 관련 API를 추가할 수 있습니다 (예: 사용자 정보 조회 등)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # 현재 로그인된 사용자
):
    """
    현재 로그인된 사용자의 계정을 삭제합니다.
    관련된 모든 채팅방과 메시지도 함께 삭제됩니다.
    """
    deleted = await crud_users.delete_user(db, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user account")

    return