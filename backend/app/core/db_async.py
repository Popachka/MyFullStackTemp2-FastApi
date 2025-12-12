from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings


def _build_async_url() -> str:
    url = str(settings.SQLALCHEMY_DATABASE_URI)
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg_async://", 1)
    return url


async_engine = create_async_engine(_build_async_url(), echo=False)
async_session_maker = async_sessionmaker[AsyncSession](
    async_engine, class_=AsyncSession, expire_on_commit=False
)

