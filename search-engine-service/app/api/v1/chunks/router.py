from fastapi import (
    UploadFile,
    APIRouter, 
    HTTPException, 
    File,
    status,
    Depends, 
    Request
)
from qdrant_client import QdrantClient

import uuid
from pathlib import Path
import tempfile
from typing import List

from app.streaming.publisher import EventPublisher
from app.api.v1.chunks.schemas import UploadChunks
from app.logger import get_logger

from app.core.security.schemas import UnauthorizedMessage
from app.core.llm.provider import LargeModel
from app.core.llm.dependecies import get_llm_model
from app.core.qdrant.dependecies import get_qdrant_client
from app.core.security.dependencies import get_token
from app.core.tasks import TaskTracker
from app.core.schemas import TaskUploadingProgress


router = APIRouter(
    prefix='/chunks',
    tags=["chunks"]
)
logger = get_logger(__name__)


@router.post(
    "/hypothetical-queries",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_hypotical_querys(
    query: str,
    llm: LargeModel = Depends(get_llm_model),
    token: str = Depends(get_token)
):
    """
    Эндпоинт для 
    """
    try:
        result = await llm.fetch_hypotical_query(query)
        return result
    except Exception as e:
        logger.error("Error processing the chunk, detail: \n %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing the chunk"
        )

@router.post(
    "/",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def create_chunk(
    upload: UploadChunks,
    qdrant: QdrantClient = Depends(get_qdrant_client),
    token: str = Depends(get_token)
):
    collections = qdrant.get_collections()
    if upload.collection_name not in [col.name for col in collections.collections]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Collection does not exist"
        )
    
    task_id = str(uuid.uuid4())
    
    await TaskTracker.create_task(
        task_id=task_id,
        metadata={"type": "uploading_chunks", "doc_name": upload.document_name}
    )
    
    await EventPublisher.publish_event(
        "task.upload_chunks",
        {
            "task_id": task_id,
            "collection_name": upload.collection_name,
            "tags": upload.tags,
            "description": upload.description,
            "chunks_data": upload.chunks,
            "document_name": upload.document_name
        }
    )
    
    return task_id


@router.patch(
    "/{chunk_id}",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def patch_chunk(chunk_id: str):
    ...

@router.put(
    "/{chunk_id}",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def patch_chunk(chunk_id: str):
    ...
    


@router.delete(
    "/delete-chunk",
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def delete_chunk():
    ...



