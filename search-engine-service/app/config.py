from pydantic_settings import BaseSettings
from pydantic import BaseModel

from typing import Dict, List
from enum import Enum

class LlmInterface(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"

from functools import lru_cache


# class PingData(BaseModel):
#     path: str
#     host: str
#     model_name: str

# class PingConfig(BaseModel):
#     ollama: PingData
#     openai: PingData

class Settings(BaseSettings):
    # Подключение к postgres
    # DB_NAME: str
    # DB_USER: str
    # DB_PASS: str
    # DB_HOST: str
    # DB_PORT: str
    TOKEN: str
    
    # redis 
    REDIS_EXPIRE: int = 3600
    
    QDRANT_BASE_URL: str
    # QDRANT_API_KEY: str
    
    LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    
    v1_prefix: str = "/api/v1"
    v2_prefix: str = "/api/v2"
    project_title: str = "search-engine-service"
    
    DENSE_WEIGHT: float = 0.7
    SPARSE_WEIGHT: float = 0.3
    RERANK_TOP_K: int = 5
    
    PRIORITY_LLM_INTERFACE: str
    
    
    PRIORITY_LLM_INTERFACE: LlmInterface = LlmInterface.OPENAI
    
    OPENAI_LLM_BASE_URL: str
    OPENAI_LLM_MODEL_NAME: str
    
    OLLAMA_LLM_BASE_URL: str
    OLLAMA_LLM_MODEL_NAME: str
    
    EMBEDDING_SERVICE: str
    EMBEDDING_SERVICE_TOKEN: str
    
    dense_model_name: str = "FRIDA"
    
    REDIS_URL: str
    
    @property
    def RESERVE_INTERFACE(self,) -> LlmInterface:
        if self.PRIORITY_LLM_INTERFACE == LlmInterface.OPENAI:
            return LlmInterface.OLLAMA
        return LlmInterface.OPENAI
        
    
    @property
    def PING_SETTINGS(self,) -> Dict[str, Dict[str, str]]: # -> PingConfig:
        settings = {
            "ollama": {
                "path": "/api/tags",
                "host": self.OLLAMA_LLM_BASE_URL,
                "model_name": self.OLLAMA_LLM_MODEL_NAME
            },
            "openai": {
                "path": "/models",
                "host": self.OPENAI_LLM_BASE_URL,
                "model_name": self.OLLAMA_LLM_MODEL_NAME
            } 
        }
        return settings
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache
def get_settings() -> Settings:
    return Settings()
