from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import ChatRoom, User # User 모델도 필요할 수 있습니다.
from app.schemas.room import RoomCreate # RoomCreate 스키마 임포트

# ID로 방을 조회하는 함수 (기존 get_room이 이 역할을 했다면 이름을 변경)
async def get_room_by_id(db: AsyncSession, room_id: int):
    result = await db.execute(select(ChatRoom).filter(ChatRoom.id == room_id))
    return result.scalars().first()

# --- 새로 추가할 함수: 이름으로 방 조회 ---
async def get_room_by_name(db: AsyncSession, room_name: str):
    result = await db.execute(select(ChatRoom).filter(ChatRoom.name == room_name))
    return result.scalars().first()

# --- 방 생성 함수 ---
# current_user.id를 creator_id로 받도록 명확히 정의
async def create_chat_room(db: AsyncSession, room: RoomCreate, creator_id: int):
    db_room = ChatRoom(name=room.name, created_by=creator_id) # created_by에 creator_id 매핑
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room

# --- 다른 rooms crud 함수들도 필요하다면 여기에 추가 ---
async def get_all_rooms(db: AsyncSession):
    result = await db.execute(select(ChatRoom))
    return result.scalars().all()

# --- 채팅방 삭제 함수 (간결화) ---
async def delete_room(db: AsyncSession, room_id: int):
    """
    주어진 room_id에 해당하는 채팅방을 삭제합니다.
    ChatRoom 모델의 cascade 설정에 따라 해당 방의 모든 메시지도 함께 삭제됩니다.
    """
    result = await db.execute(select(ChatRoom).filter(ChatRoom.id == room_id))
    room = result.scalars().first()
    if room:
        await db.delete(room)
        await db.commit() # 변경사항 커밋
        return True
    return False
