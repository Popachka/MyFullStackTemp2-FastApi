from fastapi import APIRouter, Depends, Request
from pydantic.networks import EmailStr
from sqlmodel import SQLModel
from aiogram import Bot

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email
from app.core.config import settings
from app.bot.main import build_bot

router = APIRouter(prefix="/utils", tags=["utils"])


class BotInfoResponse(SQLModel):
    username: str | None = None
    enabled: bool = False


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check")
async def health_check() -> bool:
    return True


@router.get("/bot-info", response_model=BotInfoResponse)
async def get_bot_info(request: Request) -> BotInfoResponse:
    """
    Get Telegram bot public information (username).
    """
    if not settings.TELEGRAM_ENABLED or not settings.TELEGRAM_BOT_TOKEN:
        return BotInfoResponse(enabled=False)
    
    # Пытаемся использовать существующий бот из app.state
    bot: Bot | None = getattr(request.app.state, "bot", None)
    
    if bot:
        try:
            bot_info = await bot.get_me()
            return BotInfoResponse(
                username=bot_info.username,
                enabled=True
            )
        except Exception:
            # Если ошибка с существующим ботом, создаем новый временный
            pass
    
    # Если бота нет в state, создаем временный для получения информации
    temp_bot = None
    try:
        temp_bot = build_bot()
        bot_info = await temp_bot.get_me()
        username = bot_info.username if bot_info else None
        return BotInfoResponse(
            username=username,
            enabled=True
        )
    except Exception:
        return BotInfoResponse(enabled=False)
    finally:
        # Закрываем сессию временного бота, если он был создан
        if temp_bot and hasattr(temp_bot, "session") and temp_bot.session:
            try:
                await temp_bot.session.close()
            except Exception:
                pass
