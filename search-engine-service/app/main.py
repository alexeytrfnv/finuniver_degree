from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from faststream import FastStream

from contextlib import asynccontextmanager
from typing import AsyncIterable

from app.config import get_settings
from app.api.v1.subrouter import subrouter as subrouter_v1
from app.streaming.broker import broker
from app.redis import redis_service

from fastapi.middleware.cors import CORSMiddleware

from app.core.tasks import TaskTracker
from app.core.schemas import TaskUploadingProgress
from app.streaming.publisher import EventPublisher



settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterable[None]:
    """
        Жизненный цикл приложения
    """
    await broker.start()
    yield
    await broker.stop()
    

    
def create_application() -> FastAPI:
    _app = FastAPI(
        title=settings.project_title,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_methods = ["*"],
        allow_headers = ["*"]
    )

    _app.mount(settings.v1_prefix, subrouter_v1)
    return _app


app = create_application()


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready"}
