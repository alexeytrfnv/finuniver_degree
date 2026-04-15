from fastapi import FastAPI

from contextlib import asynccontextmanager
from typing import AsyncIterable

from src.api.v1.router import v1_sub_router
from src.config import config


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterable[None]:
    yield


def create_application() -> FastAPI:
    _app = FastAPI(
        lifespan=lifespan, title=config.app_title, docs_url=None, redoc_url=None
    )
    _app.mount(config.app_v1_prefix, v1_sub_router)
    return _app


app = create_application()

app.mount(config.app_v1_prefix, v1_sub_router)
