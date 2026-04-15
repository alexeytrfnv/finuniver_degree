from fastapi import status

from src.api.v1.exceptions.base import BaseException


class EmbeddingExption(BaseException):
    def __init__(self):
        super().__init__(
            detail="Embedding text problem",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )