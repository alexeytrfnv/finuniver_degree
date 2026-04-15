from pydantic import BaseModel

class UnauthorizedMessage(BaseModel):
    detail: str = "Bearer token missing or unknown"
