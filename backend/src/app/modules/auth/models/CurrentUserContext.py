from uuid import UUID
from sqlmodel import SQLModel

class CurrentUserContext(SQLModel):
    session_id: str

    user_id: UUID
    username: str
    is_superuser: bool
    is_totp_enabled: bool = False

    avatar_url: str | None = None
