from uuid import UUID

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings


class StartTokenError(Exception):
    """Generic deep link token error."""


class StartTokenExpired(StartTokenError):
    """Token expired."""


def _get_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt="tg-start")


def generate_start_token(user_uuid: UUID) -> str:
    serializer = _get_serializer()
    return serializer.dumps({"user_id": str(user_uuid)})


def verify_start_token(token: str, max_age: int = 600) -> UUID:
    serializer = _get_serializer()
    try:
        data = serializer.loads(token, max_age=max_age)
    except SignatureExpired as exc:
        raise StartTokenExpired("Token expired") from exc
    except BadSignature as exc:
        raise StartTokenError("Invalid token signature") from exc

    try:
        return UUID(data["user_id"])
    except (KeyError, ValueError) as exc:
        raise StartTokenError("Invalid token payload") from exc

