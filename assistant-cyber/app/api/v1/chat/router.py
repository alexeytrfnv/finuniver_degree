from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import func

from typing import Any

from app.api.v1.chat.schemas import QueryDialogRequest, DialogSearchSettings
from app.core.retrievel.search import SearchDeps
from app.config import get_settings, PromptTemplate
from app.core.llm.provider import OllamaModelChatDeps
from app.api.v1.dependecies import SessioDeps
from app.database.service import FeedService, QueryService
from app.config import get_settings



config = get_settings()
router = APIRouter(
    prefix="/chat"
)

@router.post("/streaming/")
async def post_streaming_queries(
    search_settings: DialogSearchSettings, 
    dialog: QueryDialogRequest, 
    engine: SearchDeps,
    llm: OllamaModelChatDeps, 
    session: SessioDeps
) -> Any:
    time_start = func.now()
    question = dialog.messages[-2]["content"]
    
    retrieved_documents = await engine.search(
        search_settings, question
    )
    
    if retrieved_documents:
        docs_context = "\n\n".join(
            doc["metadata"]["payload"] for doc in retrieved_documents
        )
        messages = [
            {"role": "system", "content": PromptTemplate.SYSTEM_TEMPLATE}
        ]
        messages.extend([
            message for message in dialog.messages[:-2]
        ])
        messages.append(
            {
                "role": "user",
                "content": PromptTemplate.CONTEXT_HUMAN_TEMPLATE.format(
                    context_str=docs_context, query=question
                ),
            }
        )
    else:
        messages = [
            {"role": "system", "content": PromptTemplate.NO_CONTEXT_TEMPLATE},
            {"role": "user", "content": f"no_think Question: {question}"},
        ]
    
    async def generate_answer():
        temp_answer = ""
        
        async for chunk in llm.astream(messages[-1]["content"]):
            if hasattr(chunk, "content") and chunk.content:
                if not chunk.content in ["<think>", "</think>"]:
                    chunk_temp = chunk.content
                    temp_answer += chunk_temp
                    
                    yield chunk_temp.encode("utf-8")
            
        await QueryService.add(
            session=session,
            email=search_settings.email,
            query=question,
            chunks=retrieved_documents,
            llm_answer=temp_answer,
            created_at=time_start
        )
        
    return StreamingResponse(generate_answer(), media_type="text/plain")