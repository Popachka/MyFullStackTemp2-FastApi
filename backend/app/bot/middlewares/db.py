from collections.abc import Awaitable, Callable
from typing import Any
import logging

from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        async with self.session_maker() as session:
            try:
                data["session"] = session
                return await handler(event, data)
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

