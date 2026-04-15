from pydantic_settings import BaseSettings
from typing import Optional, Dict
from dataclasses import dataclass

from urllib.parse import quote_plus
from functools import lru_cache

class LlmInterface:
    BASE="base"
    RESERVE="reserve"

class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

    LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"    
    
    TITLE: str = "assistant-pd-service"
    DESCRIPTION: str = "Сервис для взимодействия с помощником"
    
    RETRIEVE_LIMIT: int = 2
    MINIMAL_SIMILIARITY_SCORE: float = 0.1
    
    SEARCH_SERVICE_URL: str
    BASE_COLLECTION_NAME: Optional[str]
    
    BASE_MODEL_URL: str
    BASE_MODEL_NAME: str
    
    RESERVE_MODEL_URL: str
    RESERVE_MODEL_NAME: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{quote_plus(self.DB_PASS)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    
    @property
    def PING_SETTINGS(self,) -> Dict[str, Dict[str, str]]: # -> PingConfig:
        settings = {
            "base": {
                "path": "/api/tags",
                "host": self.BASE_MODEL_URL,
                "model_name": self.BASE_MODEL_NAME
            },
            "reserve": {
                "path": "/api/tags",
                "host": self.RESERVE_MODEL_URL,
                "model_name": self.RESERVE_MODEL_NAME
            } 
        }
        return settings
    
    
    
    class Config:
        env_file=".env"
        extra="allow"
        
@dataclass
class PromptTemplate:
    SYSTEM_TEMPLATE: str = """
    
    """

    NO_CONTEXT_TEMPLATE: str = """
    Ты — ассистент компании «СОГАЗ».
    Пользователь задал вопрос, но в базе знаний не найдено релевантных документов.

    Твоя задача — вежливо сообщить об этом и помочь сформулировать уточнение.

    Формат ответа:
    В моей базе знаний нет достаточной информации, чтобы ответить на ваш вопрос о «{query}».

    Чтобы я мог помочь, пожалуйста:
    1. 🔍 Уточните, о каком продукте или направлении страхования идёт речь.
    2. ✏ Переформулируйте вопрос — добавьте больше деталей (например: тарифы, заявление, правила и т.д.).

    Говори дружелюбно, кратко и только на русском языке.
    """

    HUMAN_TEMPLATE: str = """
    ответь на вопрос исходя из контекста, ничего не выдумывай.
    
    вопрос: {query}
    
    контекст{context_str}

    """

    CONTEXT_HUMAN_TEMPLATE: str = """
    📚 КОНТЕКСТ:
    {context_str}

    ❓ВОПРОС:
    {query}

    🎯 ИНСТРУКЦИЯ:
    Отвечай строго на русском языке, используя ТОЛЬКО информацию из контекста.
    Не добавляй ничего из внешних источников или догадок.

    Если контекст частично релевантен:
    - Чётко укажи, какие аспекты можешь объяснить.
    - Назови, какой информации не хватает для полного ответа.
    - Дай максимально точный и полезный ответ на основе имеющегося контекста.
    """


@lru_cache
def get_settings() -> Settings:
    return Settings()