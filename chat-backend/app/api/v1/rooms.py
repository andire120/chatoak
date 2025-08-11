from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.db.models import User # current_user의 타입 힌트를 위해
from app.crud import rooms as crud_rooms
from app.crud import messages as crud_messages # 메시지 CRUD가 있다면
from app.schemas.room import RoomCreate, RoomDisplay
from app.schemas.message import MessageDisplay # 메시지 스키마가 있다면
from app.core.dependencies import get_current_user # 올바른 경로로 수정

router = APIRouter()

@router.get("/rooms", response_model=List[RoomDisplay])
async def get_all_chat_rooms(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """모든 채팅방 목록을 조회합니다."""
    rooms = await crud_rooms.get_all_rooms(db)
    return rooms

@router.post("/rooms", response_model=RoomDisplay, status_code=status.HTTP_201_CREATED)
async def create_new_chat_room(room: RoomCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """새로운 채팅방을 생성합니다."""
    # 1. 동일한 이름의 방이 이미 존재하는지 확인: get_room_by_name 함수 사용
    existing_room = await crud_rooms.get_room_by_name(db, room_name=room.name)
    if existing_room:
        raise HTTPException(status_code=400, detail="동일한 이름의 채팅방이 이미 존재합니다.")

    # 2. 새로운 방 생성: user_id 대신 creator_id로 current_user.id 전달
    return await crud_rooms.create_chat_room(db, room=room, creator_id=current_user.id)

@router.get("/rooms/{room_id}/messages", response_model=List[MessageDisplay])
async def get_room_messages(room_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """특정 채팅방의 메시지 목록을 조회합니다."""
    # 룸 ID로 조회: get_room_by_id 함수 사용
    room = await crud_rooms.get_room_by_id(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    messages = await crud_messages.get_messages_for_room(db, room_id=room_id) # crud_messages도 확인 필요
    return messages

@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chatroom(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 ID의 대화방을 삭제합니다.
    - 대화방의 생성자만 삭제할 수 있습니다.
    - CASCADE 설정에 따라 대화방의 모든 메시지도 함께 삭제됩니다.
    """
    # 1. 대화방 조회
    room = await crud_rooms.get_room_by_id(db, room_id)

    # 2. 대화방이 존재하는지 확인
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found."
        )

    # 3. 현재 사용자가 대화방의 생성자인지 확인
    if room.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this chat room."
        )

    # 4. 대화방 삭제 및 커밋
    try:
        await crud_rooms.delete_room(db, room)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the chat room: {str(e)}"
        )
    
    return {"message": "Chat room deleted successfully."}
