from typing import Dict, Optional, Any
import datetime

from app.core.schemas import (
    TaskUploadingProgress,
    DocumentUploadingStatus
)
from app.redis import redis_service
from app.streaming.publisher import EventPublisher


class TaskTracker:
    TASK_PREFIX = "task:"
    TASK_TTL = 86400 # сутки
    
    @staticmethod
    async def create_task(task_id: str, metadata: Dict = None) -> TaskUploadingProgress:
        now = datetime.datetime.now(datetime.timezone.utc)
        task = TaskUploadingProgress(
            task_id=task_id,
            status=DocumentUploadingStatus.PENDING,
            progress=0,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        await redis_service.set(
            f"{TaskTracker.TASK_PREFIX}{task_id}",
            task.model_dump_json(),
            expire=TaskTracker.TASK_TTL
        )
        return task
    
    @staticmethod
    async def get_task(task_id: str) -> Optional[TaskUploadingProgress]:
        task_data = await redis_service.get(f"{TaskTracker.TASK_PREFIX}{task_id}")
        
        if not task_data:
            return None
        
        return TaskUploadingProgress.model_validate_json(task_data)

    @staticmethod
    async def update_progress(
        task_id: str,
        status: DocumentUploadingStatus = None,
        progress: int = None,
        result: Any = None,
        error: str = None
    ) -> None:
        task: TaskUploadingProgress = await TaskTracker.get_task(task_id)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if status:
            task.status = status
        if progress is not None:
            task.progress = min(100, max(0, progress))
        if result is not None:
            task.result = result
        if error:
            task.error = error
        
        task.updated_at = datetime.datetime.now(datetime.timezone.utc)
        await redis_service.set(
            f"{TaskTracker.TASK_PREFIX}{task_id}",
            task.model_dump_json(),
            expire=TaskTracker.TASK_TTL
        )
        
        await EventPublisher.publish_event(
            f"task.updated.{task_id}",
            {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress
            }
        )        
    
    @staticmethod
    async def complete_task(task_id: str, result: str) -> None:
        await TaskTracker.update_progress(
            task_id,
            status=DocumentUploadingStatus.COMPLETED,
            progress=100,
            result=result
        )
    
    @staticmethod
    async def fail_task(task_id: str, error: str) -> None:
        await TaskTracker.update_progress(
            task_id,
            status=DocumentUploadingStatus.FAILED,
            error=error
        )
    
    @staticmethod
    async def cancel_task(task_id: str, result: str) -> None:
        await TaskTracker.update_progress(
            task_id,
            status=DocumentUploadingStatus.CANCELLED,
        )