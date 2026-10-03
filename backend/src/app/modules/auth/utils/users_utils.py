import hashlib
from typing import Any, cast
from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.app.core.config import settings
from src.app.deps.dbs import db_session
from src.app.modules.auth.models.Users import User


async def get_user_by_id(session: db_session, id: UUID) -> User | None:
    result = await session.exec(
        select(User)
        .options(selectinload(cast(Any, User.backup_codes)))
        .options(selectinload(cast(Any, User.wallet)))
        .where(User.id == id)
    )
    user = result.one_or_none()
    return user

async def get_user_by_username(session: db_session, username: str) -> User | None:
    result = await session.exec(select(User).where(User.username == username))
    user = result.one_or_none()
    return user

async def get_user_by_email(session: db_session, email: str) -> User | None:
    blind_index = get_blind_index(email)
    result = await session.exec(select(User).where(User.email_blind_index == blind_index))
    return result.one_or_none()


SECRET_KEY = settings.SECRET_KEY

def get_blind_index(data: str) -> str:
    return hashlib.sha256(f"{SECRET_KEY}{data}".encode()).hexdigest()