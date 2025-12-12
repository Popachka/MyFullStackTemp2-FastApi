import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel

from app.api.deps import SessionDep, get_current_active_superuser
from app.bot.security import generate_start_token
from app.models import User


class StartTokenResponse(SQLModel):
    token: str


router = APIRouter(tags=["debug"])


@router.get(
    "/debug-token",
    response_model=StartTokenResponse,
    dependencies=[Depends(get_current_active_superuser)],
)
def generate_debug_token(user_id: uuid.UUID, session: SessionDep) -> StartTokenResponse:
    """
    Temporary helper to generate Telegram start token for a given user.
    Restricted to superusers.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = generate_start_token(user_id)
    return StartTokenResponse(token=token)

