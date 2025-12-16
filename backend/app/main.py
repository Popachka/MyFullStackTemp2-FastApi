import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from typing import AsyncIterator

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.bot.main import build_bot, build_dispatcher
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    # Some internal routes (webhook) may have no tags; fall back to name only.
    first_tag = route.tags[0] if route.tags else "route"
    return f"{first_tag}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.bot = None
    app.state.dp = None
    app.state.bot_task = None
    bot_started = False

    if settings.TELEGRAM_ENABLED:
        try:
            bot = build_bot()
            dp = build_dispatcher()
            app.state.bot = bot
            app.state.dp = dp
            if settings.RUN_BOT_POLLING:
                await bot.delete_webhook(drop_pending_updates=True)
                app.state.bot_task = asyncio.create_task(dp.start_polling(bot))
                bot_started = True
                logger.info("Telegram bot started in polling mode")
            else:
                webhook_url = f"{settings.SERVER_HOST.rstrip('/')}{settings.API_V1_STR}/telegram-webhook"
                await bot.set_webhook(
                    url=webhook_url,
                    secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
                    drop_pending_updates=False,
                )
                bot_started = True
                logger.info("Telegram bot webhook set to %s", webhook_url)
        except TelegramNetworkError as exc:
            logger.error(
                "Telegram network error during startup: %s. Bot disabled.", exc
            )
        except (
            Exception
        ) as exc:  # catch other init errors (bad token, middleware, etc.)
            logger.exception(
                "Telegram bot initialization failed: %s. Bot disabled.", exc
            )
            app.state.bot = None
            app.state.dp = None
            app.state.bot_task = None

    try:
        yield
    finally:
        if not settings.RUN_BOT_POLLING and app.state.bot:
            try:
                await app.state.bot.delete_webhook(drop_pending_updates=False)
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to delete webhook on shutdown: %s", exc)

        if app.state.bot_task:
            app.state.bot_task.cancel()
            with suppress(asyncio.CancelledError):
                await app.state.bot_task

        if app.state.bot:
            await app.state.bot.session.close()
            logger.info("Telegram bot shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_STR)
# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.post(
    f"{settings.API_V1_STR}/telegram-webhook",
    include_in_schema=False,
)
async def telegram_webhook(request: Request) -> dict[str, bool]:
    if (
        not settings.TELEGRAM_ENABLED
        or not getattr(request.app.state, "bot", None)
        or not getattr(request.app.state, "dp", None)
    ):
        # bot disabled or not initialized; ignore webhook
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot disabled",
        )

    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret"
        )

    update = await request.json()
    bot: Bot = request.app.state.bot
    dp: Dispatcher = request.app.state.dp
    await dp.feed_webhook_update(bot=bot, update=update)
    return {"ok": True}
