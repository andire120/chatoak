import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()

class RedisManager:
    def __init__(self):
        self.redis_client = None

    async def connect(self):
        if not self.redis_client:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            try:
                await self.redis_client.ping()
                print("Redis 연결 성공!")
            except redis.exceptions.ConnectionError as e:
                print(f"Redis 연결 실패: {e}")
                self.redis_client = None

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def publish(self, channel: str, message: str):
        if self.redis_client:
            await self.redis_client.publish(channel, message)

    async def subscribe(self, channel: str):
        if self.redis_client:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        return None

    async def unsubscribe(self, pubsub, channel: str):
        if self.redis_client and pubsub:
            await pubsub.unsubscribe(channel)

redis_manager = RedisManager()