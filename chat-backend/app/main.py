from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.services.redis_manager import redis_manager
from app.api.v1 import auth, rooms, websockets

# 애플리케이션 시작/종료 시 이벤트 처리
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 DB 초기화 및 Redis 연결
    print("서비스 시작 중...")
    await init_db()
    await redis_manager.connect()
    yield
    # 종료 시 Redis 연결 해제
    print("서비스 종료 중...")
    await redis_manager.disconnect()

app = FastAPI(lifespan=lifespan)

# CORS 설정 (프론트엔드와 백엔드 간 통신 허용)
origins = [
    "http://localhost:5173",  # React 개발 서버 기본 포트
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(auth.router, prefix="", tags=["Auth"]) # '/register', '/login'
app.include_router(rooms.router, prefix="", tags=["Rooms"]) # '/rooms', '/rooms/{room_id}/messages'
app.include_router(websockets.router) # '/ws/chat/{room_id}'