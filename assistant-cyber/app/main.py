from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from typing import AsyncIterable

from app.api.v1.chat.router import router as chat_router
from app.config import get_settings

config = get_settings()


@asynccontextmanager
async def lifespan() -> AsyncIterable[None]:
    yield

def create_application() -> FastAPI:
    _app = FastAPI(
        title=config.TITLE,
        description=config.DESCRIPTION
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_methods = ["*"],
        allow_headers = ["*"]
    )
    _app.include_router(chat_router)
    
    return _app

app = create_application()


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready"}

