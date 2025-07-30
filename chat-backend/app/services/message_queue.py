import asyncio
from collections import deque
from typing import Dict, Any

class MessageQueue:
    def __init__(self):
        self.queue: deque[Dict[str, Any]] = deque()
        self.lock = asyncio.Lock()
        self.processing = False

    async def add_message(self, message: Dict[str, Any]):
        async with self.lock:
            self.queue.append(message)
            if not self.processing:
                self.processing = True
                asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        from app.db.database import AsyncSessionLocal
        from app.crud.messages import create_chat_message
        from app.schemas.message import MessageCreate

        while True:
            async with self.lock:
                if not self.queue:
                    self.processing = False
                    break
                message_data = self.queue.popleft()
            
            async with AsyncSessionLocal() as db:
                try:
                    # MessageCreate 스키마에 맞게 데이터 준비
                    msg_schema = MessageCreate(content=message_data["content"])
                    await create_chat_message(db, msg_schema, message_data["room_id"], message_data["sender_id"])
                    print(f"Message saved to DB: {message_data['content']}")
                except Exception as e:
                    print(f"Failed to save message to DB: {e}")
                    # 재시도 로직 추가 가능

            await asyncio.sleep(0.1) # 비동기 I/O를 위한 작은 지연

message_queue = MessageQueue()