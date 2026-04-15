from pydantic import BaseModel

from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime


class DocumentUploadingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    

class TaskUploadingProgress(BaseModel):
    task_id: str
    status: DocumentUploadingStatus
    progress: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: dict = {}


