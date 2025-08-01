from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.db.models import User # current_user의 타입 힌트를 위해
from app.crud import rooms as crud_rooms
from app.crud import messages as crud_messages # 메시지 CRUD가 있다면
from app.schemas.room import RoomCreate, RoomDisplay
from app.schemas.message import MessageDisplay # 메시지 스키마가 있다면
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/rooms", response_model=List[RoomDisplay])
async def get_all_chat_rooms(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    rooms = await crud_rooms.get_all_rooms(db)
    return rooms

@router.post("/rooms", response_model=RoomDisplay, status_code=status.HTTP_201_CREATED)
async def create_new_chat_room(room: RoomCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. 동일한 이름의 방이 이미 존재하는지 확인: get_room_by_name 함수 사용
    existing_room = await crud_rooms.get_room_by_name(db, room_name=room.name)
    if existing_room:
        raise HTTPException(status_code=400, detail="동일한 이름의 채팅방이 이미 존재합니다.")

    # 2. 새로운 방 생성: user_id 대신 creator_id로 current_user.id 전달
    return await crud_rooms.create_chat_room(db, room=room, creator_id=current_user.id)

@router.get("/rooms/{room_id}/messages", response_model=List[MessageDisplay])
async def get_room_messages(room_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 룸 ID로 조회: get_room_by_id 함수 사용
    room = await crud_rooms.get_room_by_id(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    messages = await crud_messages.get_messages_for_room(db, room_id=room_id) # crud_messages도 확인 필요
    return messages

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = await crud_rooms.get_room_by_id(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat room not found")

    # TODO: 여기에서 room.created_by와 current_user.id를 비교하여 권한 확인 로직 추가
    # 예: if room.created_by != current_user.id:
    #       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this room")

    deleted = await crud_rooms.delete_room(db, room_id=room_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete chat room")

    return