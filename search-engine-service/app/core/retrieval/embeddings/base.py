import numpy as np
import requests
import httpx

from dataclasses import dataclass
from typing import List, Dict, Optional, Iterator

from app.config import get_settings

config = get_settings()


@dataclass
class SparceEmbedding:
    indices: List[int]
    values: List[float]

    def as_object(self) -> Dict[str, List[float]]:
        return {
            "values": self.values,
            "indices": self.indices,
        }

    def as_dict(self) -> Dict[int, float]:
        return {idx: val for idx, val in zip(self.indices, self.values)}


class SparseEmbeddingText:
    host: str = config.EMBEDDING_SERVICE
    secret_token: str = config.EMBEDDING_SERVICE_TOKEN

    @classmethod
    async def embed(cls, texts: List[str]) -> List[SparceEmbedding]:
        async with httpx.AsyncClient() as session:
            result = await session.post(
                f"{cls.host}/api/v1/sparse/embed-texts",
                json={"texts": texts},
                headers={"authorization": f"Bearer {cls.secret_token}"}
            )
            output = result.json()

        return list(output["data"])
    
    @classmethod
    async def query_embed(cls, query: str) -> SparceEmbedding:
        async with httpx.AsyncClient() as session:
            result = await session.post(
                f"{cls.host}/api/v1/sparse/embed-query",
                json={"query": query},
                headers={"authorization": f"Bearer {cls.secret_token}"}
            )
            output = result.json()

        return SparceEmbedding(**output["data"])


class DenseEmbeddingText:
    host: str = config.EMBEDDING_SERVICE
    secret_token: str = config.EMBEDDING_SERVICE_TOKEN

    @classmethod
    async def embed(cls, texts: List[str]) -> List[List[float]]:
        async with httpx.AsyncClient() as session:
            result = await session.post(
                f"{cls.host}/api/v1/frida/embed-texts",
                json={"texts": texts},
                headers={"authorization": f"Bearer {cls.secret_token}"}
            )
            output = result.json()

        return list(output["data"])

    @classmethod
    async def query_embed(cls, query: List[str]) -> List[float]:
        async with httpx.AsyncClient() as session:
            result = await session.post(
                f"{cls.host}/api/v1/frida/embed-query",
                json={"query": query},
                headers={"authorization": f"Bearer {cls.secret_token}"}
            )
            output = result.json()

        return output["data"]
