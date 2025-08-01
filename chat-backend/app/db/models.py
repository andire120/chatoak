# app/db/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # User가 생성한 방들 (User 삭제 시 ChatRoom도 함께 삭제)
    created_rooms = relationship(
        "ChatRoom",
        back_populates="creator",
        cascade="all, delete-orphan" # User 삭제 시, 해당 User가 만든 방도 함께 삭제
    )
    # User가 보낸 메시지들 (User 삭제 시 메시지도 함께 삭제)
    sent_messages = relationship(
        "Message",
        back_populates="sender",
        cascade="all, delete-orphan" # User 삭제 시, 해당 User가 보낸 메시지도 함께 삭제
    )

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id")) # 방을 생성한 User의 ID

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ChatRoom과 User 간의 관계 (방 생성자)
    creator = relationship("User", back_populates="created_rooms")

    # ChatRoom과 Message 간의 관계 (방 안에 있는 메시지들)
    messages = relationship(
        "Message",
        back_populates="room",
        order_by="Message.timestamp", # 메시지를 시간 순서대로 정렬 (오래된 것이 위로)
        cascade="all, delete-orphan" # ChatRoom 삭제 시, 해당 방의 모든 메시지도 함께 삭제
    )

class ChatMessage(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False) # 메시지가 속한 방 ID
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)   # 메시지를 보낸 User ID
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) # 메시지 전송 시간

    # Message와 ChatRoom 간의 관계
    room = relationship("ChatRoom", back_populates="messages")

    # Message와 User 간의 관계
    sender = relationship("User", back_populates="sent_messages")