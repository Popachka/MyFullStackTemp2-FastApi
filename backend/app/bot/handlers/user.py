import random

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.bot.security import StartTokenError, StartTokenExpired, verify_start_token
from app.core.config import settings
from app.models import Item, User


router = Router(name="user")


def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="👤 Профиль")
    kb.button(text="📦 Мои предметы")
    kb.button(text="➕ Добавить Random Item")
    kb.button(text="🚪 Выйти")
    kb.adjust(1, 2, 1)
    return kb.as_markup(resize_keyboard=True)


async def _safe_answer(message: Message, text: str, reply_markup=None) -> None:
    try:
        await message.answer(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        return


@router.message(CommandStart())
async def handle_start(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
) -> None:
    print("[START] received /start", {"from_user": message.from_user.id if message.from_user else None, "args": command.args if command else None})
    payload = (command.args or "").strip() if command else ""
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id is None:
        print("[START] missing telegram_id")
        return

    if payload:
        print("[START] payload detected", {"payload": payload})
        try:
            user_uuid = verify_start_token(payload)
        except StartTokenExpired:
            print("[START] token expired")
            await _safe_answer(
                message, "Срок действия ссылки истёк. Пожалуйста, запросите новую."
            )
            return
        except StartTokenError:
            print("[START] token invalid")
            await _safe_answer(
                message,
                "Ссылка недействительна. Пожалуйста, запросите новую в личном кабинете.",
            )
            return

        try:
            result = await session.exec(select(User).where(User.telegram_id == telegram_id))
            existing_by_tg = result.first()

            if existing_by_tg and existing_by_tg.id != user_uuid:
                print("[START] telegram already bound to another user", {"existing_user_id": existing_by_tg.id, "payload_user_id": user_uuid})
                await _safe_answer(
                    message,
                    "Этот Telegram уже привязан к другому аккаунту. "
                    "Если это ошибка — отвяжите его в профиле.",
                )
                return

            target_user = await session.get(User, user_uuid)
            if not target_user:
                print("[START] target user not found", {"user_uuid": str(user_uuid)})
                await _safe_answer(
                    message, "Пользователь не найден. Получите новую ссылку на сайте."
                )
                return

            if target_user.telegram_id and target_user.telegram_id != telegram_id:
                print("[START] account already bound to another telegram", {"target_user_id": target_user.id, "existing_tg": target_user.telegram_id, "new_tg": telegram_id})
                await _safe_answer(
                    message, "Этот аккаунт уже привязан к другому Telegram."
                )
                return

            target_user.telegram_id = telegram_id
            session.add(target_user)
            await session.commit()
            await session.refresh(target_user)
            print("[START] binding successful", {"user_id": target_user.id, "telegram_id": telegram_id})
            await _safe_answer(
                message,
                f"Привет! Вы авторизованы как {target_user.email}.\nЧто будем делать?",
                reply_markup=get_main_keyboard(),
            )
        except SQLAlchemyError:
            print("[START] db error, rolling back")
            await session.rollback()
            await _safe_answer(
                message, "Сервис временно недоступен. Пожалуйста, попробуйте позже."
            )
        return

    print("[START] no payload; regular start", {"telegram_id": telegram_id})
    try:
        result = await session.exec(select(User).where(User.telegram_id == telegram_id))
        existing_user = result.first()
    except SQLAlchemyError:
        print("[START] db error on regular start")
        await _safe_answer(
            message, "Сервис временно недоступен. Пожалуйста, попробуйте позже."
        )
        return

    if existing_user:
        print("[START] existing user found", {"user_id": existing_user.id})
        await _safe_answer(
            message,
            f"Привет! Вы авторизованы как {existing_user.email}.\nЧто будем делать?",
            reply_markup=get_main_keyboard(),
        )
        return

    print("[START] new user, show registration prompt")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Зарегистрироваться на сайте",
                    url=settings.FRONTEND_HOST,
                )
            ]
        ]
    )
    await _safe_answer(
        message,
        "Привет! Чтобы пользоваться ботом, зарегистрируйтесь на сайте и нажмите кнопку "
        "«Подключить Telegram» в личном кабинете.",
        reply_markup=keyboard,
    )


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, session: AsyncSession) -> None:
    result = await session.exec(select(User).where(User.telegram_id == message.from_user.id))
    user = result.first()

    if not user:
        await message.answer("Вы не авторизованы. Нажмите /start")
        return

    await message.answer(
        "📋 Ваши данные:\n"
        f"ID: `{user.id}`\n"
        f"Email: {user.email}\n"
        f"Active: {user.is_active}\n"
        f"Superuser: {user.is_superuser}",
        reply_markup=get_main_keyboard(),
    )


@router.message(F.text == "➕ Добавить Random Item")
async def create_random_item(message: Message, session: AsyncSession) -> None:
    result = await session.exec(select(User).where(User.telegram_id == message.from_user.id))
    user = result.first()

    if not user:
        await message.answer("Сначала авторизуйтесь!")
        return

    random_id = random.randint(1, 1000)
    new_item = Item(
        title=f"Тестовый предмет #{random_id}",
        description=f"Создан через бота в {random_id}",
        owner_id=user.id,
    )

    session.add(new_item)
    await session.commit()

    await message.answer(
        f"✅ Предмет {new_item.title} успешно создан!",
        reply_markup=get_main_keyboard(),
    )


@router.message(F.text == "📦 Мои предметы")
async def list_items(message: Message, session: AsyncSession) -> None:
    user_result = await session.exec(select(User).where(User.telegram_id == message.from_user.id))
    user = user_result.first()

    if not user:
        await message.answer("Вы не авторизованы. Нажмите /start")
        return

    items_result = await session.exec(select(Item).where(Item.owner_id == user.id))
    items = items_result.all()

    if not items:
        await message.answer("У вас пока нет предметов 🤷‍♂️", reply_markup=get_main_keyboard())
        return

    text_lines = ["📦 Ваши предметы:"]
    for item in items:
        text_lines.append(f"- {item.title} (ID: {str(item.id)[:8]}...)")

    await message.answer("\n".join(text_lines), reply_markup=get_main_keyboard())


@router.message(F.text == "🚪 Выйти")
async def logout(message: Message, session: AsyncSession) -> None:
    result = await session.exec(select(User).where(User.telegram_id == message.from_user.id))
    user = result.first()

    if not user:
        await message.answer("Вы и так не авторизованы.", reply_markup=ReplyKeyboardRemove())
        return

    user.telegram_id = None
    session.add(user)

    try:
        await session.commit()
        await message.answer(
            "✅ Вы успешно вышли из аккаунта.\n"
            "Бот больше не имеет доступа к вашим данным.",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception:
        await session.rollback()
        await message.answer("Ошибка при выходе. Попробуйте позже.")