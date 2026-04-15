from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field
from typing import List, Dict
import re

from app.logger import get_logger

logger = get_logger(__name__)


class Questions(BaseModel):
    questions: List[str] = Field(default=[], description="Список вопросов")


class HypoticalQuerysChain:
    def __init__(self, model) -> None:
        self.model = model
        self.questions_parser = JsonOutputParser(pydantic_object=Questions)

    async def __clean_think_tags(self, message: str | AIMessage) -> str | AIMessage:
        """Асинхронная очистка тегов <think>"""
        if hasattr(message, "content"):
            text = message.content
            cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
            message.content = cleaned_text
            return message
        return message

    async def __hypoticatical_querys_proceess(self, context: List[str] = None) -> PromptTemplate:
        """Создание промпта (синхронная операция)"""
        prompt = PromptTemplate(
            template="""
            Ты - система для извлечения информации.
            Тебе дан текст. На основе только этого текста нужно создать список вопросов,
            на которые однозначно есть ответы внутри текста.
            Если в тексте недостаточно информации или нет фактов, не придумывай -- просто верни пустой список.
            нужно извлечь из текста как можно больше вопросов, ответ, на который, содержится в тексте

            Важно:
            - Всегда возвращай JSON.
            - "questions" должен быть списком строк.
            - Не добавляй ничего вне JSON.
            - вопросы должны быть исключительно на русском языка
            сам текст
            {query}
            {format_instuction}
            """,
            input_variables=["query"],
            partial_variables={
                "format_instuction": self.questions_parser.get_format_instructions()
            },
        )
        return prompt

    async def aget_hypothetical_questions(self, query: str) -> Dict[str, any]:
        """Асинхронное получение гипотетических вопросов"""
        prompt = await self.__hypoticatical_querys_proceess()
        
        # Создаем асинхронный chain
        chain = (
            prompt
            | self.model
            | RunnableLambda(self.__clean_think_tags)
            | self.questions_parser
        )
        
        # Используем ainvoke для асинхронного выполнения
        result = await chain.ainvoke({"query": query})
        logger.info(result)
        logger.info(type(result))
        result["query"] = query
        return result

    # Оставляем синхронную версию для обратной совместимости (опционально)
    # def get_hypothetical_questions(self, query: str) -> Dict[str, any]:
    #     """Синхронная версия (deprecated, используйте aget_hypothetical_questions)"""
    #     prompt = self.__hypoticatical_querys_proceess()
    #     chain = (
    #         prompt
    #         | self.model
    #         | RunnableLambda(lambda x: self.__clean_think_tags_sync(x))
    #         | self.questions_parser
    #     )
    #     result = chain.invoke({"query": query})
    #     result["query"] = query
    #     return result

    # def __clean_think_tags_sync(self, message: str | AIMessage) -> str | AIMessage:
    #     """Синхронная версия очистки тегов"""
    #     if hasattr(message, "content"):
    #         text = message.content
    #         cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    #         message.content = cleaned_text
    #         return message
    #     return message