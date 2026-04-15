from fastapi import Depends

from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama
import httpx
import ssl

from typing import (
    List, 
    Tuple, 
    Dict, 
    Any, 
    AsyncIterator, 
    AsyncGenerator,
    Annotated,
    ForwardRef
)

from app.logger import get_logger
from app.config import get_settings, Settings, LlmInterface

logger = get_logger(__name__)
config = get_settings()

class OllamaModelChat:
    def __init__(self, config: Settings):
        self.config = config
        self.ping_settings = self.config.PING_SETTINGS
            
    async def __ping_ai_model(self,) -> LlmInterface:
        """
        Пингуем llm, проверка на доступность модели
        в случае неудачи, переход на резерв
        """
        async with httpx.AsyncClient() as session:
            try:
                status_priority = await session.get(
                    f"{self.ping_settings["base"]['host']}{self.ping_settings["base"]['path']}",
                    timeout=httpx.Timeout(1.0)
                )
                logger.info("get model %s", f"{self.ping_settings["base"]['host']}{self.ping_settings["base"]['path']}")
            
                if status_priority.status_code == 200:
                    return LlmInterface.BASE
            except Exception as e:
                logger.error("failed to fetch model %s", f"{self.ping_settings["base"]['host']}")
                
            status_reserve = await session.get(
                f"{self.ping_settings["reserve"]['host']}{self.ping_settings["reserve"]['path']}",
                timeout=httpx.Timeout(None)
            )
            logger.info("get model %s", status_reserve.status_code)
            
            if status_reserve.status_code == 200:
                return LlmInterface.RESERVE

    async def __create_ai_model(self, 
        session: httpx.AsyncClient
    ) -> ChatOllama:
        """
        Создаем объект модели
        """
        interface = await self.__ping_ai_model()
        
        if interface == LlmInterface.BASE:
            ollama_ping_settings = self.ping_settings[interface]
            return ChatOllama(
                base_url=ollama_ping_settings["host"],
                model=ollama_ping_settings["model_name"],
                http_async_client=session
            )
        
        if interface == LlmInterface.RESERVE:
            openai_ping_settings = self.ping_settings[interface]
            return ChatOllama(
                base_url=openai_ping_settings["host"],
                model=openai_ping_settings["model_name"],
                http_async_client=session
            )
            
    
    async def ainvoke(self, 
        message: str
    ) -> AIMessage:
        async with httpx.AsyncClient() as session:
            llm = await self.__create_ai_model(
                session=session
            )
            
            if llm is None:
                raise httpx.HTTPError(
                    message="Couldn't connect to llm"
                )
            
            return await llm.ainvoke(message)
    
    async def astream(self, messages):
        async with httpx.AsyncClient() as session:
            llm = await self.__create_ai_model(
                session=session
            )
            # return llm
            async for chunk in llm.astream(messages):
                yield chunk
                
                
async def get_llm_model(): #-> AsyncGenerator[OllamaModelChat, None]:
    llm_model = OllamaModelChat(config)
    
    try:
        yield llm_model
    except Exception as e:
        logger.error("problem with get model \n %s", str(e))
        raise
    

# OllamaModelChatRef = ForwardRef('OllamaModelChat')
OllamaModelChatDeps = Annotated[OllamaModelChat, Depends(get_llm_model)]