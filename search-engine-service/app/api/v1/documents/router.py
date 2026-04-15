from fastapi import (
    UploadFile,
    APIRouter, 
    HTTPException, 
    File,
    status,
    Form,
    Depends
)
from langchain_community.document_loaders import PyPDFLoader
from qdrant_client import QdrantClient

import uuid
from pathlib import Path
import tempfile
import shutil
from typing import List

from app.streaming.publisher import EventPublisher
from app.logger import get_logger

from app.core.tasks import TaskTracker
from app.core.schemas import TaskUploadingProgress
from app.core.qdrant.dependecies import get_qdrant_client


router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)
logger = get_logger(__name__)


@router.get("/uploading-status/{task_id}",
    response_model=TaskUploadingProgress
)
async def get_document_uploading_status(
    task_id: str,
):
    task = await TaskTracker.get_task(
        task_id
    )
    if not task:
        raise HTTPException(status_code=400, detail="Task not found")
    
    return task.model_dump(mode="json")


@router.post("/upload")
async def test_upload_document(
    collection_name: str = Form(...),
    tags: List[str] = Form(...),
    description: List[str] = Form(...),
    file: UploadFile = File(...),
    qdrant: QdrantClient = Depends(get_qdrant_client)
):
    collections = qdrant.get_collections()
    if collection_name not in [col.name for col in collections.collections]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Collection does not exist"
        )
    
    filename = file.filename
    media_type = file.filename.split(".")[-1].lower()
    
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=f".{media_type}"
    ) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = Path(temp_file.name)

        loader = PyPDFLoader(str(temp_file_path))
        pages = loader.load()

    logger.info(f"Загружаем {file.filename} в базу знаний")
    
    if len(pages) >= 500:
        logger.info(f"Документ {file.filename} превышает порог в 500 страниц")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="too long file"
        )

    task_id = str(uuid.uuid4())
    
    await TaskTracker.create_task(
        task_id=task_id,
        metadata={"type": "uploading_document", "doc_name": filename}
    )
    
    await EventPublisher.publish_event(
        "task.upload_document_new",
        {
            "task_id": task_id,
            "collection_name": collection_name,
            "tags": tags,
            "description": description,
            "document_data": pages,
            "document_name": filename
        }
    )
        
    return {"task_id": task_id}

@router.delete("/")
async def delete_document():
    ...