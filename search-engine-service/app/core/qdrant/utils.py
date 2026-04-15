from fastapi import HTTPException, Depends
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, models

from langchain_core.documents import Document
from fastapi import HTTPException
from qdrant_client.models import SparseVectorParams, Modifier

from typing import List, Dict
import uuid

from app.config import get_settings
from app.logger import get_logger
from app.core.qdrant.dependecies import get_qdrant_client
from app.core.retrieval.embeddings.base import (
    DenseEmbeddingText,
    SparseEmbeddingText,
    SparceEmbedding
)

config = get_settings()
logger = get_logger(__name__)


async def index_documents_hybrid(
    tags_list: List[str],
    document_name: str,
    document_chunks: List[Dict[str, str | List[str]]],
    collection_name: str,
):
    """Индексирование документов как с плотными, так и с разреженными эмбеддингами"""
    if not document_chunks:
        raise ValueError("No documents to index")

    qdrant_client = await get_qdrant_client()

    # points = []
    for chunk in document_chunks:
        # print(chunk)
        dense_embeddings = list(await DenseEmbeddingText.embed(chunk["questions"]))
        sparse_embeddings = await SparseEmbeddingText.query_embed(chunk["query"])
        # print(sparse_embeddings)
        sparse_embeddings = [sparse_embeddings] * len(dense_embeddings)
    
        for idx, (dense_emb, sparse_emb, doc) in enumerate(
            zip(dense_embeddings, sparse_embeddings, chunk["questions"])
        ):
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector={
                    "FRIDA": dense_emb,
                    "miniCOIL": sparse_emb.as_object(),
                    "metadata_vector": dense_emb,
                },
                payload={
                    "question": doc, 
                    "metadata": chunk["query"],
                    "document_name": document_name
                },
            )
            try:   
                qdrant_client.upsert(
                    collection_name=collection_name, 
                    points=[point]
                )
                logger.info(f"Indexed {len(chunk["questions"])} chunks with hybrid embeddings")

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to index documents: {str(e)}"
                )
            
async def hybrid_search(
    query: str,
    collection_name: str,
    # rerank_model: RerankType, Пока что без ранжирвования
    limit: int = 10,
    minimal_meta_score: float = 0.20,
    # filter_cond: models.Filter | None = None,
) -> List[Document]:
    """Гибридный поиск: отдельные dense/sparse запросы, нормализация, дедупликация.

    Оставлена совместимая сигнатура (query, limit). Использует глобальные
    dense_embedding_model, sparse_embedding_model и qdrant_client, как и ранее.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    

    # 1) Сгенерировать эмбеддинги
    try:
        dense_vector = await DenseEmbeddingText.query_embed(f"search_document: {query}")
    except Exception as e:
        logger.error(f"Dense embedding failed: {e}")
        raise HTTPException(status_code=500, detail="Dense embedding failed")

    sparse_vector = None
    try:
        sparse_vector = await SparseEmbeddingText.query_embed(query)
    except Exception:
        logger.warning(
            "Sparse embedding failed or not available — continuing with dense only"
        )
        
    qdrant_client: QdrantClient = await get_qdrant_client()

    # 2) Выполнить два отдельных запроса к Qdrant (dense и sparse), собрать кандидатов
    candidates = {}  # id -> {'payload':..., 'dense_score':..., 'sparse_score':...}
    # Dense search
    try:
        dense_res = qdrant_client.query_points(
            collection_name=collection_name,
            query=dense_vector,
            using=config.dense_model_name,
            with_payload=True,
            limit=max(limit, 50),
            # query_filter=filter_cond,
        )
        print(dense_res)
    except Exception as e:
        logger.exception(f"Qdrant dense query failed: {e}")
        dense_res = None

    if dense_res and getattr(dense_res, "points", None):
        for p in dense_res.points:
            pid = getattr(p, "id", None)
            if pid is None:
                continue
            payload = getattr(p, "payload", {}) or {}
            score = getattr(p, "score", None)
            entry = candidates.setdefault(pid, {"payload": payload})
            if score is not None:
                entry["dense_score"] = float(score)

    # Sparse search (если доступен)
    if sparse_vector is not None:
        try:
            # sparse_vector may provide as_object() for conversion
            sparse_query = None
            if hasattr(sparse_vector, "as_object"):
                sparse_query = models.SparseVector(**sparse_vector.as_object())
            else:
                sparse_query = sparse_vector
            sparse_res = qdrant_client.query_points(
                collection_name=collection_name,
                query=sparse_query,
                using="miniCOIL",
                with_payload=True,
                limit=max(limit, 50),
                # query_filter=filter_cond,
            )
        except Exception as e:
            logger.exception(f"Qdrant sparse query failed: {e}")
            sparse_res = None

        if sparse_res and getattr(sparse_res, "points", None):
            for p in sparse_res.points:
                pid = getattr(p, "id", None)
                if pid is None:
                    continue
                payload = getattr(p, "payload", {}) or {}
                score = getattr(p, "score", None)
                entry = candidates.setdefault(pid, {"payload": payload})
                if score is not None:
                    entry["sparse_score"] = float(score)

    # 3) Нормализация скорoв (min-max) и объединение
    dense_scores = [v.get("dense_score", 0.0) for v in candidates.values()]
    sparse_scores = (
        [v.get("sparse_score", 0.0) for v in candidates.values()] if candidates else []
    )

    def _min_max_normalize(scores):
        if not scores:
            return []
        lo = min(scores)
        hi = max(scores)
        if hi == lo:
            return [1.0 for _ in scores]
        return [(s - lo) / (hi - lo) for s in scores]

    dense_norm = _min_max_normalize(dense_scores)
    sparse_norm = (
        _min_max_normalize(sparse_scores) if sparse_scores else [0.0] * len(dense_norm)
    )

    # assign normalized
    for (pid, entry), d_n, s_n in zip(candidates.items(), dense_norm, sparse_norm):
        entry["dense_norm"] = d_n
        entry["sparse_norm"] = s_n

    # combine with weights (configurable via settings if present)
    dense_w = getattr(config, "DENSE_WEIGHT", 0.7)
    sparse_w = getattr(config, "SPARSE_WEIGHT", 0.3)
    for pid, entry in candidates.items():
        entry["combined"] = dense_w * entry.get(
            "dense_norm", 0.0
        ) + sparse_w * entry.get("sparse_norm", 0.0)

    # 4) Сортировка и выбор топ кандидатов (для опционального rerank)
    ranked = sorted(
        candidates.items(), key=lambda kv: kv[1].get("dense_score", 0.0), reverse=True
    )
    top_candidates = ranked[: max(limit, getattr(config, "RERANK_TOP_K", 20))]

    # 6) Финальная дедупликация по хешу текста и формирование документов
    def _hash_text(text: str) -> str:
        import hashlib

        return hashlib.sha1(text.strip().encode("utf-8")).hexdigest()

    seen_hashes = set()
    results = []
    for pid, entry in top_candidates:
        meta_score = entry["dense_score"]
        meta = {}
        if meta_score > minimal_meta_score:
            raw = entry["payload"].get("question", "")
            h = _hash_text(raw)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            
            meta["payload"] = entry["payload"].get("metadata", {})
            meta["score"] = {
                "dense_score": entry["dense_score"],
                # "sparse_corm": entry["sparse_score"],
                # "dense_norm": entry["dense_norm"],
                "sparse_norm": entry["sparse_norm"],
                "combined": entry["combined"],
            }
            results.append(Document(id=h, page_content=raw, metadata=meta))
            if len(results) >= limit:
                break

    return results
