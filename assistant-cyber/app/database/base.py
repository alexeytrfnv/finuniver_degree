from sqlalchemy import select, insert, update
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import func
from typing import TypeVar, Generic, Type


ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseService(Generic[ModelType]):
    model: Type[ModelType]

    @classmethod
    async def find_by_id(cls, session, model_id: int):
        query = select(cls.model).filter_by(id=model_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, session, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, session,  **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add(cls, session, **data):
        query = insert(cls.model).values(**data)
        await session.execute(query)
        await session.commit()