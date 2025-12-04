from typing import Optional

import redis.asyncio as aioredis

from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if self.redis:
            return await self.redis.get(key)
        return None

    async def set(self, key: str, value: str, expire: int = 300):
        """Set value in Redis with TTL (default 5 minutes)"""
        if self.redis:
            await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        """Delete key from Redis"""
        if self.redis:
            await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self.redis:
            return await self.redis.exists(key) > 0
        return False


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency for Redis client"""
    return redis_client
