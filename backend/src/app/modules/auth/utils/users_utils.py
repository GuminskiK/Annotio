from typing import Optional

from sqlmodel import select
import hashlib
from src.app.core.config import settings
from src.app.modules.auth.models.Users import User
from src.app.deps.dbs import db_session
from uuid import UUID

async def get_user_by_id(session: db_session, id: UUID) -> User | None:
    result = await session.exec(select(User).where(User.id == id))
    user = result.one_or_none()
    return user

async def get_user_by_username(session: db_session, username: str) -> User | None:
    result = await session.exec(select(User).where(User.username == username))
    user = result.one_or_none()
    return user

async def get_user_by_email(session: db_session, email: str) -> Optional[User]:
    blind_index = get_blind_index(email)
    result = await session.exec(select(User).where(User.email_blind_index == blind_index))
    return result.one_or_none()


SECRET_KEY = settings.SECRET_KEY

def get_blind_index(data: str) -> str:
    return hashlib.sha256(f"{SECRET_KEY}{data}".encode()).hexdigest()