from pydantic import BaseModel


class CreateCollection(BaseModel):
    name: str
    chunk_size: int
    
class Collection(BaseModel):
    name: str
    
class DeleteCollection(BaseModel):
    name: str
    
class CollectionStatus(BaseModel):
    detail: str