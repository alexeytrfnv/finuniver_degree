from fastapi import HTTPException, Depends, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from typing import Optional

from app.config import get_settings

get_bearer_token = HTTPBearer(auto_error=False)
config = get_settings()


async def get_token(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:
    if auth is None or not (token := auth.credentials) == config.TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token missing or unknown"
        )
    return token
