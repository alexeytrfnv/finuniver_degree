from sentence_transformers import CrossEncoder

from pathlib import Path

from src.config import config

class CrossEncoderReranker:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.cross_encoder = CrossEncoder(
            model_name_or_path=self.model_path,
            max_length=512
        )


    def rerank(
        self, query: str, documents: list[str], top_k=None
    ) -> list[tuple[str, float]]:
        predicted_result = self.cross_encoder.rank(query, documents)
        filtered_data = sorted(
            predicted_result,
            key=lambda x: x["corpus_id"],
        )
        data = [float(value["score"]) for value in filtered_data]

        return data
    
cross_encoder_model = CrossEncoderReranker(config.path_to_cross_encoder_model)
