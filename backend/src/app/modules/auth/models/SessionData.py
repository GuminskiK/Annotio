from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from app.modules.auth.models.Users import Role

class SessionData(BaseModel):
    session_id: str
    created_at: str
    device: str
    ip: str | None

    user_id: UUID
    username: str
    role: Role
    is_totp_enabled: bool = False
    # is_banned: bool = False

    avatar_url: str | None = None
