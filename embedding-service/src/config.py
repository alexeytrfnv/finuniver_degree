from pydantic_settings import BaseSettings

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    app_title: str = "lins-embedding-service"
    app_v1_prefix: str = "/api/v1"
    app_description: str = """
    Сервис для работы с эмбеддниговыми моделями
    
    Ранжирование: 
     rubert-mini-frida
     cross-msmarco

    Эмбеддинг:
     FRIDA
     multilingual-e5-base
     minicoil-v1
    """
    # base path to models
    base_path_to_model: Path = Path(__file__).parent / "models"

    # reranker bi model
    bi_encoder_model_name: str = "rubert-mini-frida"
    path_to_bi_encoder_model: Path = base_path_to_model / bi_encoder_model_name

    cross_encoder_model_name: str = "cross-msmarco"
    path_to_cross_encoder_model: Path = base_path_to_model / cross_encoder_model_name

    # dense embedding model
    dense_embedding_model_name: str = "multilingual-e5-base"
    path_to_dense_embdedding_model: Path = (
        base_path_to_model / dense_embedding_model_name
    )

    # sparse embedding model
    sparse_embedding_model_name: str = "minicoil-v1"
    path_to_sparse_embedding_model: Path = (
        base_path_to_model / sparse_embedding_model_name
    )
    
    frida_embedding_model_name: str = "FRIDA"
    path_to_frida_model: Path = (
        base_path_to_model / frida_embedding_model_name
    )
    
    # giga_embedding_model_name: str = "Giga-Embeddings-instruct"
    # path_to_giga_model: Path = (
    #     base_path_to_model / giga_embedding_model_name
    # )


class Settings(BaseSettings):
    SECRET_TOKEN: str
    SPARSE_MODEL: str
    DENSE_MODE: str
    RERANK_MODEL: str

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
config = Config()
