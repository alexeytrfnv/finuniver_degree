from fastapi import APIRouter, Depends, HTTPException, status

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, Modifier


from app.logger import get_logger
from app.core.qdrant.utils import hybrid_search
from app.core.qdrant.dependecies import get_qdrant_client

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

logger = get_logger(__name__)

@router.get("/")
async def search_info(
    query: str,
    collection_name: str,
    limit: int,
    minimal_meta_score: float,
    qdrant: QdrantClient = Depends(get_qdrant_client),
):
    collections = qdrant.get_collections().collections
    exisisting_collections = [collection.name for collection in collections]
    
    if not collection_name in exisisting_collections:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"the collection {collection_name} not found"
        )
        
    result = await hybrid_search(
        query,
        collection_name,
        limit,
        minimal_meta_score
    )
    return result