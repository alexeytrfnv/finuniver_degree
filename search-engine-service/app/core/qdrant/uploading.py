from fastapi import Depends
from pydantic import BaseModel

from typing import Dict, List
import asyncio
import json

from typing import Dict, List, Any

from app.streaming.broker import broker

from app.logger import get_logger
from app.config import get_settings 
from app.core.tasks import TaskTracker
from app.core.llm.provider import LargeModel
from app.core.llm.dependecies import get_llm_model
from app.core.schemas import DocumentUploadingStatus
from app.core.qdrant.utils import index_documents_hybrid
from app.core.retrieval.splitter.base import RecursiveChunking

logger = get_logger(__name__)
config = get_settings()

@broker.subscriber("task.upload_chunks")
async def upload_chunks(
    message: Dict
):
    if message is None:
        logger.error("upload_chunks: received empty message")
         
    if isinstance(message, (bytes, bytearray)):
        try:
            message = json.loads(message.decode("utf-8"))
        except Exception as e:
            logger.error("uplaod_chunks: failed to decode bytes message: \n %s", e)
            return
    elif isinstance(message, str):
        try:
            message = json.loads(message)
        except Exception as e:
            logger.error("uplaod_chunks: received non-JSON string message %s", e)
            return
    if not isinstance(message, dict):
        logger.error("uplaod_chunks: unexpected message type %s", type(message))
        
    task_id = message.get("task_id")
    chunks = message.get("chunks_data")
    document_name = message.get("document_name")
    collection_name = message.get("collection_name")
    
    try:
        await TaskTracker.update_progress(
            task_id,
            status=DocumentUploadingStatus.PROCESSING,
            progress=50
        )
        await index_documents_hybrid(
            tags_list=[],
            document_name=document_name,
            document_chunks=chunks,
            collection_name=collection_name
        )
        await TaskTracker.complete_task(
            task_id,
            result=chunks
        )
        
    except Exception as e:
        logger.error("Exception %s", e)
        await TaskTracker.fail_task(
            task_id,
            error=str(e)
        )
        
    

@broker.subscriber("task.upload_document_new")
async def upload_document(
    message: Dict
):
    if message is None:
        logger.error("upload_document: received empty message")
    
    if isinstance(message, (bytes, bytearray)):
        try:
            message = json.loads(message.decode("utf-8"))
        except Exception as e:
            logger.error("upload_document: failed to decode bytes message: \n %s", e)
            return
    elif isinstance(message, str):
        try:
            message = json.loads(message)
        except Exception as e:
            logger.error("uplaod_document: received non-JSON string message %s", e)
            return
    if not isinstance(message, dict):
        logger.error("upload_document: unexpected message type %s", str(message))
    
    task_id = message.get("task_id")
    document = message.get("document_data")
    document_name = message.get("document_name")
    collection_name = message.get("collection_name")
    
    llm = await get_llm_model()
    
    splitter = RecursiveChunking(
        chunk_overlap=30
    )
    
    try:
        chunks = await splitter.chunk(document)
        doc_len = len(chunks["data"])
        processed_chunks = []
        
        await TaskTracker.update_progress(
            task_id,
            status=DocumentUploadingStatus.PROCESSING,
            progress=0
        )
        
        for idx, chunk in enumerate(chunks["data"]):
            await TaskTracker.update_progress(
                task_id,
                progress=int(((idx+1)/doc_len) * 100),
            )
            result = await llm.fetch_hypotical_query(chunk)
            processed_chunks.append(result)
        
        await index_documents_hybrid(
            [],
            document_name,
            processed_chunks,
            collection_name,
        )
            
        await TaskTracker.complete_task(
            task_id,
            result=processed_chunks
        )
            
    except Exception as e:
        logger.error("Exception %s", e)
        await TaskTracker.fail_task(
            task_id,
            error=str(e)
        )