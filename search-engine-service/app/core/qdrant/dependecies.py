from fastapi import Depends
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, models

from app.config import get_settings

config = get_settings()

qdrant_client = QdrantClient(
    url=config.QDRANT_BASE_URL,
    # api_key=config.QDRANT_API_KEY
)

async def get_qdrant_client() -> QdrantClient:
    return qdrant_client

