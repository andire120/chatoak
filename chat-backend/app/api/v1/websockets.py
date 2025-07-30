from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.crud import users as crud_users
from app.crud import rooms as crud_rooms
from app.services.redis_manager import redis_manager
from app.services.message_queue import message_queue
from app.core.security import decode_access_token
from app.db.models import User
import json
import asyncio

router = APIRouter()

# 활성 WebSocket 연결을 관리하는 딕셔너리
# Key: room_id, Value: List[WebSocket]
active_connections: dict[int, list[WebSocket]] = {}

@router.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = Query(...), # URL 쿼리 파라미터로 JWT 토큰 받기
    db: AsyncSession = Depends(get_db)
):
    # 1. JWT 인증
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication token")
        return

    username = payload.get("sub")
    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token does not contain username")
        return

    current_user: User = await crud_users.get_user_by_username(db, username=username)
    if not current_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        return

    # 2. 채팅방 유효성 검사
    room = await crud_rooms.get_room(db, room_id=room_id)
    if not room:
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA, reason="Chat room not found")
        return

    await websocket.accept()
    print(f"WebSocket accepted for room {room_id} and user {username}")

    # 3. Redis pub/sub 구독
    # Redis 구독은 각 WebSocket 연결별로 이루어져야 합니다.
    pubsub = await redis_manager.subscribe(f"chat_{room_id}")
    if not pubsub:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Failed to connect to Redis")
        return

    # 4. 활성 연결 추가
    if room_id not in active_connections:
        active_connections[room_id] = []
    active_connections[room_id].append(websocket)

    try:
        # 비동기로 메시지 수신 (클라이언트 -> 서버)
        async def receive_messages():
            while True:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                content = message_data.get("message")
                if content:
                    # Redis를 통해 메시지 발행
                    message_to_publish = {
                        "username": current_user.username,
                        "message": content
                    }
                    await redis_manager.publish(f"chat_{room_id}", json.dumps(message_to_publish))

                    # DB에 저장하기 위해 큐에 추가
                    await message_queue.add_message({
                        "room_id": room_id,
                        "sender_id": current_user.id,
                        "content": content
                    })

        # 비동기로 메시지 구독 (Redis -> 서버 -> 클라이언트)
        async def listen_to_redis():
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
                if message and message["type"] == "message":
                    decoded_message = message["data"]
                    # 현재 방의 모든 연결된 클라이언트에게 메시지 전송
                    for connection in active_connections[room_id]:
                        try:
                            await connection.send_text(decoded_message)
                        except RuntimeError as e: # WebSocket 연결이 이미 닫혔을 경우
                            print(f"Failed to send to a client, connection likely closed: {e}")
                            # 연결이 끊어진 경우 active_connections에서 제거하는 로직 필요
                            if connection in active_connections[room_id]:
                                active_connections[room_id].remove(connection)
                await asyncio.sleep(0.01) # CPU 과부하 방지

        # 두 개의 비동기 태스크를 동시에 실행
        await asyncio.gather(receive_messages(), listen_to_redis())

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for room {room_id} and user {username}")
    except RuntimeError as e: # WebSocket closed
        print(f"RuntimeError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 연결 종료 시 활성 연결에서 제거
        if websocket in active_connections.get(room_id, []):
            active_connections[room_id].remove(websocket)
            if not active_connections[room_id]: # 방에 아무도 없으면 방 제거
                del active_connections[room_id]
        await redis_manager.unsubscribe(pubsub, f"chat_{room_id}")
        await pubsub.close()
        print(f"Connection closed and cleaned up for room {room_id} and user {username}")