from pydantic import BaseModel

from typing import List

from src.service.embeddings.schemas import SparceEmbedding


class DenseEmbeddingListData(BaseModel):
    texts: List[str]


class DenseEmbeddingQuery(BaseModel):
    query: str


class DenseEmbedTextsRes(BaseModel):
    status: bool
    data: List[List[float]]


class DenseEmbedQueryRes(BaseModel):
    status: bool
    data: List[float]
    
class FridaTokenCount(BaseModel):
    status: bool
    data: int | None


class SparseEmbeddingQuery(BaseModel):
    query: str


class SparseEmbeddingListData(BaseModel):
    texts: List[str]


class SparseEmbedQueryRes(BaseModel):
    status: bool
    data: SparceEmbedding


class SparseEmbedTextsRes(BaseModel):
    status: bool
    data: List[SparceEmbedding]
    
class Document(BaseModel):
    text: str
    chunk_overlap: int

class RecursiveChunked(BaseModel):
    status: bool
    data: List[str]