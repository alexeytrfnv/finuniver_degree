from pydantic import BaseModel

from typing import List

class DocumentMeta(BaseModel):
    collection_name: str
    tags: List[str]
    description: List[str]