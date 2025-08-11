# app/crud/rooms.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import ChatRoom
from app.schemas.room import RoomCreate

async def get_room_by_id(db: AsyncSession, room_id: int):
    """ID로 방을 조회합니다."""
    result = await db.execute(select(ChatRoom).filter(ChatRoom.id == room_id))
    return result.scalars().first()

async def get_room_by_name(db: AsyncSession, room_name: str):
    """이름으로 방을 조회합니다."""
    result = await db.execute(select(ChatRoom).filter(ChatRoom.name == room_name))
    return result.scalars().first()

async def create_chat_room(db: AsyncSession, room: RoomCreate, creator_id: int):
    """새로운 대화방을 생성합니다."""
    db_room = ChatRoom(name=room.name, created_by=creator_id)
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room

async def get_all_rooms(db: AsyncSession):
    """모든 대화방 목록을 조회합니다."""
    result = await db.execute(select(ChatRoom))
    return result.scalars().all()

async def delete_room(db: AsyncSession, room: ChatRoom):
    """대화방을 삭제합니다."""
    await db.delete(room)
    await db.commit()
