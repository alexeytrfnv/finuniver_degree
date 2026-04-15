from pydantic import BaseModel

from typing import List


class RerankData(BaseModel):
    query: str
    chuncks: List[str]


class RerankResult(BaseModel):
    status: bool
    rerank_score: List[float]
