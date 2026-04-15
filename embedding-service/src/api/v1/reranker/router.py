from fastapi import APIRouter, HTTPException, status, Depends

from src.api.v1.reranker.schemas import RerankData, RerankResult
from src.service.reranker.bi_encoder import bi_reranker
from src.service.reranker.cross_encoder import cross_encoder_model
from src.service.utils.auth import get_token

import logging


logger = logging.getLogger(__file__)

router = APIRouter(
    tags=["text reranker endpoints"],
)


@router.post("/bi/rerank-chunks", response_model=RerankResult)
async def reranker_chuncks_bi(
    data: RerankData,
    token: str = Depends(get_token),
):
    """
    Эндпоинт для ранжирования текста\n
        query: str вопрос
        chuncks: list список чанков текста

    """
    try:
        reranked_data = bi_reranker.rerank(data.query, data.chuncks)
    except Exception as e:
        logger.error("reranker exceptins %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервиса",
        )

    return {"status": True, "rerank_score": reranked_data}


@router.post("/cross/rerank-chunks", response_model=RerankResult)
async def reranker_chuncks_cross_encoder(
    data: RerankData,
    token: str = Depends(get_token),
):
    """
    Эндпоинт для ранжирования текста\n
        query: str вопрос
        chuncks: list список чанков текста
    """
    try:
        reranked_data = cross_encoder_model.rerank(data.query, data.chuncks)
    except Exception as e:
        logger.error("reranker exceptins %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервиса",
        )

    return {"status": True, "rerank_score": reranked_data}
