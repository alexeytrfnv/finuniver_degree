from typing import Any, Dict
import json

from app.streaming.broker import broker
from app.logger import get_logger

logger = get_logger(__name__)

class EventPublisher:
    
    @staticmethod
    async def publish_event(channel: str, message: Dict[str, Any]):
        try:
            await broker.publish(message, channel=channel)
            logger.info("Event publeshed to %s: %s", channel, type(message))
        except Exception as e:
            logger.error("Filed to piblish event:\n %s", e)
    