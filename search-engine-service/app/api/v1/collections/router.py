from fastapi import (
    APIRouter, 
    HTTPException, 
    status,
    Depends, 
)
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, Modifier

from typing import List

from app.api.v1.collections.schemas import (
    CreateCollection, 
    Collection,
    CollectionStatus,
    DeleteCollection
)

from app.logger import get_logger
from app.config import get_settings

from app.core.security.schemas import UnauthorizedMessage
from app.core.security.dependencies import get_token
from app.core.qdrant.dependecies import get_qdrant_client


router = APIRouter(
    prefix='/collections',
    tags=["collections"]
)

logger = get_logger(__name__)
config = get_settings()

@router.get("/",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    response_model=List[Collection]
)
async def get_collections(
    qdrant: QdrantClient = Depends(get_qdrant_client),
    token: str = Depends(get_token)
):# ->:
    try:
        collections = qdrant.get_collections().collections
        return collections
    except Exception as e:
        logger.error("couldn't get qdrant collections %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="couldn't get qdrant collections"
        )

@router.post("/",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    response_model=CollectionStatus
)
async def create_collection(
    collection: CreateCollection,
    qdrant: QdrantClient = Depends(get_qdrant_client),
    token: str = Depends(get_token)
):
    collections = qdrant.get_collections().collections
    exisisting_collections = [collection.name for collection in collections]
    
    if collection.name in exisisting_collections:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"the collection {collection.name} has already been created"
        )
    
    try:
        qdrant.create_collection(
            collection_name=collection.name,
            vectors_config={
                config.dense_model_name: VectorParams(
                    size=collection.chunk_size,
                    distance=Distance.COSINE
                ),
                "metadata_vector": VectorParams(
                    size=collection.chunk_size,
                    distance=Distance.COSINE
                )   
            },
            sparse_vectors_config={
                "miniCOIL": SparseVectorParams(modifier=Modifier.IDF)
            },
        )
        
        # return {"detail": f"the collection {collection.name} was successfully created"}
        return CollectionStatus(
            detail=f"the collection {collection.name} was successfully created"
        )
    except Exception as e:
        logger.error("the collection has not been created %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="the collection has not been created"
        )
    
   

 
@router.delete("/",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)},
    response_model=CollectionStatus
)
async def delete_collection(
    collection: DeleteCollection,
    token: str = Depends(get_token),
    qdrant: QdrantClient = Depends(get_qdrant_client),
):
    try:
        result = qdrant.delete_collection(collection.name)
        if result:
            return CollectionStatus(
                detail=f"{collection.name}'s collection has been successfully deleted"
            )
            
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection does not exist"
        )
            
    except Exception as e:
        logger.error("couldn't delete collection %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="couldn't delete collection"
        )