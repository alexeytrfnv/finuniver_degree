from pydantic import BaseModel, Field

from app.config import get_settings

config = get_settings()

class SearchSettings(BaseModel):
    query: str
    collection_name: str = config.BASE_COLLECTION_NAME
    limit: int = Field(
        default=config.RETRIEVE_LIMIT,
        ge=1,
        le=50
    )
    minimal_meta_score: float = Field(
        default=config.MINIMAL_SIMILIARITY_SCORE,
        ge=0,
        le=1
    )