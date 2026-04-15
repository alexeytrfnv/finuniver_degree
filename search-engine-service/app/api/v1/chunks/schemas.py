from pydantic import BaseModel

from typing import List


class Chunks(BaseModel):
    questions: List[str]
    query: str

    
class UploadChunks(BaseModel):
    tags: List[str]
    description: List[str]
    collection_name: str
    document_name: str
    chunks: List[Chunks]