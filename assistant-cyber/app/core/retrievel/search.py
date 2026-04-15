from fastapi import Depends
import httpx

from typing import Annotated, AsyncGenerator,List, Dict, Any

from app.config import get_settings
from app.logger import get_logger
from app.core.llm.provider import OllamaModelChatDeps
from app.core.retrievel.schemas import SearchSettings


config = get_settings()
logger = get_logger(__name__)

class SearchEngine:
    def __init__(self,):
        
        self.search_service_url: str = config.SEARCH_SERVICE_URL
        self.collection_name: str = config.BASE_COLLECTION_NAME
    
    async def search(self,
        search_settings: SearchSettings,
        query: str
    ) -> List[Dict[str, Any] | Any]:
        params = search_settings.model_dump()
        params["query"] = query
        
        async with httpx.AsyncClient() as session:
            result = await session.get(
                f"{self.search_service_url}/api/v1/search/",
                params=params
            )
            if result.status_code == 200:
                return result.json()
            return []


async def get_search_engine() -> AsyncGenerator[SearchEngine, None]:
    service = SearchEngine()
    try:
        yield service
    except Exception as e:
        logger.error("problem with get search data \n %s", str(e))
        # raise ValueError("problem with get search data \n %s", str(e))
        raise

SearchDeps = Annotated["SearchEngine", Depends(get_search_engine)]
    
    