from fastapi import APIRouter, HTTPException, status, Depends

from src.api.v1.embeddings.schemas import (
    DenseEmbeddingListData,
    DenseEmbeddingQuery,
    DenseEmbedTextsRes,
    DenseEmbedQueryRes,
    SparseEmbedQueryRes,
    SparseEmbeddingListData,
    SparseEmbeddingQuery,
    SparseEmbedTextsRes,
    FridaTokenCount,
    Document,
    RecursiveChunked
)
from src.service.embeddings.dense_embeddings import (
    dense_embedding_model,
    dense_frida_model
)
from src.service.embeddings.sparse_embeddings import sparse_embedding_model
from src.service.utils.auth import get_token
from src.service.utils.schemas import UnauthorizedMessage
from src.api.v1.exceptions.exceptions import (
    EmbeddingExption,
)

import logging


logger = logging.getLogger(__file__)


router = APIRouter(
    tags=["text embeddings endpoints"],
)


@router.post(
    "/frida/recursive-chunking", 
    tags=["frida-embedding-model"],
    description="chunk_size: 512\nrequire chunk_overlap",
    response_model=RecursiveChunked,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_recursive_chunks(
    data: Document, token: str = Depends(get_token)
):
    try:
        texts = dense_frida_model.recusrive_chunking(
            data.text,
            data.chunk_overlap
        )
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()
    
    return {"status": True, "data": texts}

@router.post(
    "/frida/count-tokens", 
    tags=["frida-embedding-model"],
    response_model=FridaTokenCount,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_dense_embeddings_query(
    data: DenseEmbeddingQuery, token: str = Depends(get_token)
):
    try:
        embedded_data = dense_frida_model.count_tokens(data.query)
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()
    return {"status": True, "data": embedded_data}

@router.post(
    "/frida/embed-query", 
    tags=["frida-embedding-model"],
    response_model=DenseEmbedQueryRes,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_dense_embeddings_query(
    data: DenseEmbeddingQuery, token: str = Depends(get_token)
):
    try:
        embedded_data = dense_frida_model.query_embed(data.query)
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()
    return {"status": True, "data": embedded_data}


@router.post(
    "/frida/embed-texts", 
    tags=["frida-embedding-model"],
    response_model=DenseEmbedTextsRes,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_dense_embeddings_texts(
    data: DenseEmbeddingListData, token: str = Depends(get_token)
):
    try:
        embedded_data = dense_frida_model.embed(data.texts)
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()

    return {"status": True, "data": embedded_data}


@router.post(
    "/dense/embed-texts", 
    response_model=DenseEmbedTextsRes,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_dense_embeddings_texts(
    data: DenseEmbeddingListData, token: str = Depends(get_token)
):
    try:
        embedded_data = dense_embedding_model.embed(data.texts)
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()

    return {"status": True, "data": embedded_data}


@router.post(
    "/dense/embed-query", 
    response_model=DenseEmbedQueryRes,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_dense_embeddings_query(
    data: DenseEmbeddingQuery, token: str = Depends(get_token)
):
    try:
        embedded_data = dense_embedding_model.query_embed(data.query)
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()
    return {"status": True, "data": embedded_data}


@router.post(
    "/sparse/embed-query", 
    response_model=SparseEmbedQueryRes,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_spase_embeddings_query(
    data: SparseEmbeddingQuery, token: str = Depends(get_token)
):
    try:
        embedded_data = sparse_embedding_model.query_embed(data.query)
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()
    return {"status": True, "data": embedded_data}


@router.post(
    "/sparse/embed-texts", 
    response_model=SparseEmbedTextsRes,
    responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)}
)
async def get_dense_embeddings(
    data: SparseEmbeddingListData, token: str = Depends(get_token)
):
    try:
        embedded_data = sparse_embedding_model.embed(data.texts)
    except Exception as e:
        logger.error("embedding exceptins %s", str(e))
        raise EmbeddingExption()
    return {"status": True, "data": embedded_data}
