from pydantic import BaseModel

class Chunk(BaseModel):
    text: str
    
# class DocChunk(BaseModel):
#     id: None | str
    