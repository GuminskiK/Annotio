import hashlib
import json
import secrets
from uuid import UUID

from sqlmodel import select

from app.core.exceptions import (
    ApiKeyNotFoundException,
    UserNotFoundException,
)
from app.modules.auth.models.APIKeys import APIKey
from app.modules.auth.models.Users import User
from app.modules.auth.models.CurrentUserContext import CurrentUserContext

from app.core.logger import get_logger
from sqlmodel.ext.asyncio.session import AsyncSession
import redis.asyncio as redis

logger = get_logger(__name__)


def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


async def generate_api_key_for_user(
    session: AsyncSession, user_id: UUID, name: str, redis: redis.Redis
):
    key = secrets.token_urlsafe(32)
    hashed = _hash_api_key(key)
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    user = result.one_or_none()
    if not user:
        logger.warning("api_key_generation_failed_user_not_found", user_id=user_id)
        raise UserNotFoundException()
    apikey = APIKey(
        name=name, hashed_key=hashed, key_hint=hashed[:4] + hashed[-4:], user_id=user_id
    )
    session.add(apikey)
    await session.commit()

    await redis.set(f"apikey:{hashed}", json.dumps({"id": str(user.id), "username": user.username, "is_superuser": user.is_superuser}))

    logger.info("api_key_saved_to_db", user_id=user_id)
    return {"id": apikey.id, "name": apikey.name, "key_hint": apikey.key_hint, "created_at": apikey.created_at, "key": key}



async def revoke_user_api_key(session: AsyncSession, user_id: UUID, key_id: UUID, redis: redis.Redis) -> None:
    result = await session.exec(
        select(APIKey).where(APIKey.user_id == user_id, APIKey.id == key_id)
    )
    apikey = result.one_or_none()
    if not apikey:
        logger.warning(
            "api_key_revoke_failed_not_found", user_id=user_id, key_id=key_id
        )
        raise ApiKeyNotFoundException()
    await session.delete(apikey)
    await session.commit()

    await redis.delete(f"apikey:{apikey.hashed_key}")

    logger.info("api_key_deleted_from_db", user_id=user_id, key_id=key_id)


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> User | None:
    hashed = _hash_api_key(api_key)
    result = await session.exec(select(APIKey).where(APIKey.hashed_key == hashed))
    apikey = result.one_or_none()
    if not apikey:
        return None
    user_result = await session.exec(select(User).where(User.id == apikey.user_id))
    user = user_result.one_or_none()
    if not user:
        return None
    return user

async def fetch_user_apikeys(user: CurrentUserContext, session: AsyncSession):
    result = await session.exec(select(APIKey).where(APIKey.user_id == user.user_id))
    apikeys = result.all()
    logger.info("user_apikeys_fetched", user_id=str(user.user_id), key_count=len(apikeys))
    return [
        {"id": k.id, "name": k.name, "key_hint": k.key_hint, "created_at": k.created_at}
        for k in apikeys
    ]


async def fetch_user_apikeys_by_id(user_id: UUID, session: AsyncSession):
    result = await session.exec(select(APIKey).where(APIKey.user_id == user_id))
    apikeys = result.all()
    logger.info("user_apikeys_fetched", user_id=str(user_id), key_count=len(apikeys))
    return [
        {"id": k.id, "name": k.name, "key_hint": k.key_hint, "created_at": k.created_at}
        for k in apikeys
    ]