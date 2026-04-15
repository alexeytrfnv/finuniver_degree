import httpx

from typing import List, Dict

from app.core.retrieval.splitter.schemas import Chunk
from app.config import get_settings

config = get_settings()

class RecursiveChunking:
    def __init__(self, chunk_overlap: int):
        self.chunk_overlap = chunk_overlap
    
    async def chunk(self, 
        texts#: List[str, str | List[Dict[str, any]]],
    ) -> List[Chunk]:
        async with httpx.AsyncClient(trust_env=False) as session:
            timeout = httpx.Timeout(10.0)
            data = [i["page_content"] for i in texts]
            joined_data = "".join(data)
            
            res = await session.post(
                f"{config.EMBEDDING_SERVICE}/api/v1/frida/recursive-chunking",
                headers={
                    "Authorization": f"Bearer {config.EMBEDDING_SERVICE_TOKEN}" 
                },
                json={
                   "text": joined_data,
                   "chunk_overlap": self.chunk_overlap
                },
                timeout=timeout
            )
            if res.status_code != 200:
                raise httpx.HTTPError(
                    message="data chunking error"
                )
            return res.json()
        
