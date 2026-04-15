from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from typing import Annotated, AsyncGenerator

from app.database.db import async_session_maker

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        
SessioDeps = Annotated[AsyncSession, Depends(get_async_session)]