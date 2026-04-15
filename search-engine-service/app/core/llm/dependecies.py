from fastapi import Depends

from app.config import get_settings
from app.core.llm.provider import LargeModel

config = get_settings()

async def get_llm_model() -> LargeModel:
    return LargeModel(config)