from faststream.redis import RedisBroker
from app.config import get_settings

settings = get_settings()

broker = RedisBroker(settings.REDIS_URL)
