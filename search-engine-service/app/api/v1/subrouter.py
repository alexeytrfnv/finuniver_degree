from fastapi import FastAPI

from app.api.v1.search.router import router as search_router
from app.api.v1.documents.router import router as documents_router
from app.api.v1.chunks.router import router as chunk_router
from app.api.v1.collections.router import router as collections_router
# from app.api.v1.chat.router import router as chat_router

from app.config import get_settings


settings = get_settings()

subrouter = FastAPI(
    title=settings.project_title
)

subrouter.include_router(search_router)
subrouter.include_router(chunk_router)
subrouter.include_router(documents_router)
subrouter.include_router(collections_router)
# subrouter.include_router(chat_router)