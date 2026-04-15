import onnxruntime as ort
from transformers import AutoTokenizer
import torch

from typing import Iterator, List
from pathlib import Path

from src.service.embeddings.schemas import SparceEmbedding
from src.config import config


class SparceEmbeddingText:
    def __init__(self, model_path: Path, device: str = "cpu", threshold: float = 0.01):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, local_files_only=True
        )
        path_to_model = model_path / "onnx" / "model.onnx"
        self.ort_session = ort.InferenceSession(path_to_model)
        self.threshold = threshold

    def embed(self, texts: list[str]) -> Iterator[SparceEmbedding]:
        # results = []
        for text in texts:
            inputs = self.tokenizer(
                text, return_tensors="np", truncation=True, padding=True
            )  # Используем NumPy для ONNX
            ort_inputs = {k: v for k, v in inputs.items()}
            ort_outs = self.ort_session.run(None, ort_inputs)

            logits = torch.tensor(ort_outs[0]).squeeze(0)
            pooled = logits.max(dim=0).values

            nonzero_indices = (pooled > self.threshold).nonzero(as_tuple=True)[0]
            values = pooled[nonzero_indices]

            yield SparceEmbedding(
                indices=nonzero_indices.tolist(), values=values.tolist()
            )

    def query_embed(self, query: str) -> SparceEmbedding:
        embeddings = self.embed([query])
        try:
            return next(embeddings)
        except StopIteration:
            raise ValueError("Sparce end")

    def __call__(self, texts: List[str]) -> Iterator[SparceEmbedding]:
        return self.embed(texts)


sparse_embedding_model = SparceEmbeddingText(config.path_to_sparse_embedding_model)
