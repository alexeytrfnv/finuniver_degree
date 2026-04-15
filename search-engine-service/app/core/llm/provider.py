from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama
import httpx

from typing import List, Tuple, Dict, Any, AsyncIterator

from app.config import get_settings, Settings, LlmInterface
from app.core.llm.chains import HypoticalQuerysChain
from app.logger import get_logger

logger = get_logger(__name__)
config = get_settings()


class LargeModel:
    def __init__(self, config: Settings):
        self.config = config
        self.ping_settings = self.config.PING_SETTINGS
            
    async def __ping_ai_model(self,) -> LlmInterface:
        """
        Пингуем llm, проверка на доступность модели
        в случае неудачи, переход на резерв
        """
        async with httpx.AsyncClient(
            trust_env=False
        ) as session:
            
            inter = self.config.PRIORITY_LLM_INTERFACE
            
            try:
                status_priority = await session.get(
                    f"{self.ping_settings[inter]['host']}{self.ping_settings[inter]['path']}",
                    timeout=httpx.Timeout(1.0)
                )
                logger.info("get model %s", f"{self.ping_settings[inter]['host']}{self.ping_settings[inter]['path']}")
            
                if status_priority.status_code == 200:
                    return self.config.PRIORITY_LLM_INTERFACE
            except Exception as e:
                logger.error("failed to fetch model %s", f"{self.ping_settings[inter]['host']}")
                
                
            reserve = self.config.RESERVE_INTERFACE
            
            status_reserve = await session.get(
                f"{self.ping_settings[reserve]['host']}{self.ping_settings[reserve]['path']}",
                timeout=httpx.Timeout(None)
            )
            logger.info("get model %s", status_reserve.status_code)
            
            if status_reserve.status_code == 200:
                return reserve

    async def __create_ai_model(self, 
        session: httpx.AsyncClient
    ) -> ChatOpenAI | ChatOllama:
        """
        Создаем объект модели
        """
        interface = await self.__ping_ai_model()
        
        if interface == LlmInterface.OLLAMA:
            ollama_ping_settings = self.ping_settings[interface]
            return ChatOllama(
                base_url=ollama_ping_settings["host"],
                model=ollama_ping_settings["model_name"],
                http_async_client=session
            )
        
        if interface == LlmInterface.OPENAI:
            openai_ping_settings = self.ping_settings[interface]
            return ChatOpenAI(
                base_url=openai_ping_settings["host"],
                model=openai_ping_settings["model_name"],
                api_key="EMPTY",
                http_async_client=session
            )
            
    
    async def ainvoke(self, 
        message: str
    ) -> AIMessage:
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            llm = await self.__create_ai_model(
                session=session
            )
            
            if llm is None:
                raise httpx.HTTPError(
                    message="Couldn't connect to llm"
                )
            
            return await llm.ainvoke(message)
    
    async def astream(self, messages):
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            llm = await self.__create_ai_model(
                session=session
            )
            # return llm
            async for chunk in llm.astream(messages):
                yield chunk
    
    async def fetch_hypotical_query(self,
        chunk: str
    ) -> List[str]:
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            llm = await self.__create_ai_model(
                session=session
            )
            if llm is None:
                raise httpx.HTTPError(
                    message="Couldn't connect to llm"
                )
                
            chain = HypoticalQuerysChain(
                model=llm
            )
            logger.info("get hypothetical queries")
            hypotical_question = await chain.aget_hypothetical_questions(
                chunk
            )
            return hypotical_question 
        
    
    async def fetch_hypotical_queries(self, 
        chunks: List[str]
    ) -> AsyncIterator[Tuple[Dict[str, Any], httpx.Response]]:
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            llm = self.__create_ai_model(
                session=session
            )
            if llm is None:
                raise httpx.HTTPError(
                    message="Couldn't connect to llm"
                )
            chain = HypoticalQuerysChain(
                model=llm
            )
            
            for idx, chunk in enumerate(chunks):
                try:
                    hypotical_question = await chain.get_hypothetical_questions(
                        chunk
                    )
                    yield chunk, hypotical_question
                except Exception as e:
                    yield chunk, e
