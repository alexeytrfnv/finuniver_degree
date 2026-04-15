from redis.asyncio import Redis, ConnectionPool

from typing import Dict, Optional, Any, List
import json

from app.config import get_settings
from app.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

class RedisService:
    
    def __init__(self, redis_url) -> None:
        self.redis = Redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def connect(self,) -> None:
        self.redis = await Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        return self.redis
    
    async def disconnect(self,) -> None:
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: Any, expire: int = settings.REDIS_EXPIRE):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(key, value, ex=expire)
        
    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
        
    async def exists(self, key: str) -> bool:
        result = await self.redis.exists(key) > 0
        return result
    

redis_service = RedisService(settings.REDIS_URL)

