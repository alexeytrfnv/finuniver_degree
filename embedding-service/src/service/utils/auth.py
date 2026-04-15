from fastapi import HTTPException, Depends, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from typing import Optional

from src.service.utils.schemas import UnauthorizedMessage
from src.config import settings

from src.service.utils.exceptions import UnauthorizedException

# We will handle a missing token ourselves
get_bearer_token = HTTPBearer(auto_error=False)


async def get_token(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> str:
    if auth is None or not (token := auth.credentials) == settings.SECRET_TOKEN:
        raise UnauthorizedException()
    return token
