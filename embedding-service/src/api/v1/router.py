from fastapi import FastAPI

from src.config import config
from src.api.v1.reranker.router import router as reranker_router
from src.api.v1.embeddings.router import router as embeddings_router


v1_sub_router = FastAPI(title=config.app_title, description=config.app_description)

v1_sub_router.include_router(reranker_router)
v1_sub_router.include_router(embeddings_router)
