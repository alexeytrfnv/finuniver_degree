from fastapi import HTTPException, status


class BaseException(HTTPException):
    def __init__(self,
        detail: str = "base exception",
        status_code: int = status.HTTP_401_UNAUTHORIZED
    ):
        super().__init__(status_code=status_code, detail=detail)

