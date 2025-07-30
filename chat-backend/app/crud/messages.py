from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.models import ChatMessage, User
from app.schemas.message import MessageCreate

async def get_messages_for_room(db: AsyncSession, room_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(ChatMessage, User.username)
        .join(User, ChatMessage.sender_id == User.id)
        .filter(ChatMessage.room_id == room_id)
        .order_by(desc(ChatMessage.timestamp)) # 최신 메시지가 먼저 오도록
        .offset(skip)
        .limit(limit)
    )
    # 조인 결과를 MessageDisplay 스키마에 맞게 변환
    return [
        {"id": msg.id, "room_id": msg.room_id, "sender_id": msg.sender_id,
         "sender_username": username, "content": msg.content, "timestamp": msg.timestamp}
        for msg, username in result.all()
    ]

async def create_chat_message(db: AsyncSession, message: MessageCreate, room_id: int, sender_id: int):
    db_message = ChatMessage(room_id=room_id, sender_id=sender_id, content=message.content)
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message