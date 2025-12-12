from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import router as root_router
from app.bot.middlewares.db import DbSessionMiddleware
from app.core.config import settings
from app.core.db_async import async_session_maker


def build_bot() -> Bot:
    # Aiogram 3.7+ requires parse_mode via default properties
    return Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    db_middleware = DbSessionMiddleware(async_session_maker)
    dp.message.middleware(db_middleware)
    dp.callback_query.middleware(db_middleware)
    dp.include_router(root_router)
    return dp

