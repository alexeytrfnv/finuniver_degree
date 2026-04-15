from sentence_transformers import SentenceTransformer, models
import numpy as np

from src.config import config
from src.service.reranker.base import BaseReranker

from pathlib import Path


class BiEncoderReranker(BaseReranker):
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.transformer = models.Transformer(model_path)
        self.word_dim = self.transformer.get_word_embedding_dimension()
        self.pooling = models.Pooling(
            word_embedding_dimension=self.word_dim,
            pooling_mode_cls_token=True,
            pooling_mode_mean_tokens=True,
            pooling_mode_max_tokens=False,
        )
        self.normalise = models.Normalize()
        self.model = SentenceTransformer(
            modules=[self.transformer, self.pooling, self.normalise]
        )

    def rerank(
        self, query: str, documents: list[str], top_k=None
    ) -> list[tuple[str, float]]:
        query_text = f"search_query: {query}"
        doc_texts = [f"search_document: {doc}" for doc in documents]

        query_emb = self.model.encode(query_text, normalize_embeddings=True)
        docs_emb = self.model.encode(doc_texts, normalize_embeddings=True)

        scores = np.dot(docs_emb, query_emb)

        results = [float(score) for score in scores]

        return results


bi_reranker = BiEncoderReranker(config.path_to_bi_encoder_model)
