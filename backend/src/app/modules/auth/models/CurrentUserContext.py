from uuid import UUID

from sqlmodel import SQLModel

from src.app.modules.auth.models.Users import Role


class CurrentUserContext(SQLModel):
    session_id: str

    user_id: UUID
    username: str
    roles: list[Role] = [Role.WORKER]
    is_superuser: bool = False
    is_totp_enabled: bool = False

    avatar_url: str | None = None
