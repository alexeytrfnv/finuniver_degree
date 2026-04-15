import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

import numpy as np
from typing import List, Optional, Iterator
from pathlib import Path

from src.config import config

    
class FridaEmbedding:
    def __init__(
        self,
        model_name: str = "ai-forever/FRIDA",
        device: str = "cpu",
        max_seq_length: int = 512,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_name))
        self.model = SentenceTransformer(str(model_name), device=device)
        self.model.max_seq_length = max_seq_length
        
    def count_tokens(self, text: str, prefix: Optional[str] = None) -> int:
        if prefix:
            text = prefix + text
        toks = self.tokenizer(text, return_attention_mask=False,
                              return_token_type_ids=False, add_special_tokens=False)
        return len(toks["input_ids"])
    
    def query_embed(self, query: str) -> list[float]:
        """Embed a search query using search_query prefix."""
        return self.model.encode(
            query,
            prompt_name="search_query",
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).tolist()

    def embed(
        self, texts: list[str], batch_size: int = 8, show_progress: bool = False
    ) -> list[list[float]]:
        """Embed documents using search_document prefix."""
        embeddings = self.model.encode(
            texts,
            prompt_name="search_document",
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def get_embedding_dim(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
    
    def recusrive_chunking(self, text: str, chunk_overlap: int) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            self.tokenizer,
            chunk_size=512,
            chunk_overlap=chunk_overlap,
        )
        texts = text_splitter.split_text(text)
        return texts
        
        


class DenseEmbeddingText:
    def __init__(
        self,
        model_path: str = "multilingual-e5-base",
        device: Optional[str] = None,
        normalize: bool = True,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(
            f"{model_path}", local_files_only=True
        )
        self.model = AutoModel.from_pretrained(model_path, local_files_only=True).to(
            self.device
        )
        self.model.eval()
        self.normalize = normalize

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            cls_embeddings = outputs.last_hidden_state[
                :, 0, :
            ]  # (batch_size, hidden_dim)

            if self.normalize:
                cls_embeddings = torch.nn.functional.normalize(
                    cls_embeddings, p=2, dim=1
                )

        return cls_embeddings.cpu().numpy()

    def embed(self, texts: List[str], batch_size: int = 32) -> Iterator[List[float]]:
        # for i in range(0, len(texts), batch_size):
        # batch = texts[i:i + batch_size]
        # batch_embeddings = self._embed_batch(batch)
        # for emb in batch_embeddings:
        # yield emb.tolist()

        for emb in self._embed_batch(texts):
            yield emb.tolist()

    def query_embed(self, query: str) -> List[float]:
        return self._embed_batch([query])[0].tolist()

    def __call__(self, texts: List[str]) -> Iterator[List[float]]:
        return self.embed(texts)


dense_embedding_model = DenseEmbeddingText(config.path_to_dense_embdedding_model)
dense_frida_model = FridaEmbedding(config.path_to_frida_model)