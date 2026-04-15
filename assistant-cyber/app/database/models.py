from sqlalchemy import String, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class Ratings(Base):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_question: Mapped[str] = mapped_column(String, nullable=False)
    llm_answer: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[str] = mapped_column(String)


class Queries(Base):
    __tablename__ = "queries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    query: Mapped[str] = mapped_column(String,)
    chunks: Mapped[dict] = mapped_column(JSONB,)
    llm_answer: Mapped[str] = mapped_column(String)