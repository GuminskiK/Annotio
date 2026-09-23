import redis.asyncio as redis
from models.Users import User
from models.SessionData import SessionData
from uuid import UUID, uuid4
from fastapi import Depends, Form, Request, Response
from datetime import timezone, datetime
from core.logger import get_logger
from app.core.config import settings
from typing import List, cast
import json
logger = get_logger(__name__)

async def createSession(
    request: Request,
    response: Response,
    user: User,
    redis: redis.Redis,
) -> None:

    generated_session_id = str(uuid4())

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else None
    device = request.headers.get("user-agent", "unknown")

    user_session = SessionData(
        session_id=generated_session_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        device=device,
        ip=ip,

        user_id=user.id,
        username=user.username,
        is_superuser=user.is_superuser,
        is_totp_enabled=user.is_totp_enabled,

        avatar_url=user.avatar_url
    )

    redis_key = f"session:{generated_session_id}"
    redis_user_key = f"user_session:{user.id}"

    await redis.set(
        name=redis_key,
        value=user_session.model_dump_json(),
        ex=settings.SESSION_TTL
    )

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=generated_session_id,
        max_age=settings.SESSION_TTL,
        httponly=settings.SESSION_HTTP_ONLY,
        secure=settings.SESSION_SECURE,
        samesite=settings.SESSION_SAME_SITE
    )

    await redis.sadd(
        redis_user_key,
        generated_session_id
    )

    logger.info("created_session_for_user", user_id=str(user.id), device=device, ip=ip, uuid=str(user.id))

async def getSessionsByUserId(
    redis: redis.Redis,
    user_id: UUID
) -> list[str]:
    session_ids = await redis.smembers(f"user_session:{user_id}")
    
    active_sessions = []
    
    for session_id in session_ids:
        exists = await redis.exists(f"session:{session_id}")
        if exists:
            active_sessions.append(session_id)
        else:
            await redis.srem(f"user_session:{user_id}", session_id)
            
    return active_sessions


async def getSessionDataByUserId(
    redis: redis.Redis,
    user_id: UUID
) -> list[SessionData]:
    session_ids = await getSessionsByUserId(redis, user_id)
    session_data_list = []
    for session_id in session_ids:
        session_data_raw = await redis.get(f"session:{session_id}")
        if session_data_raw:
            session_data = SessionData(**json.loads(session_data_raw))
            session_data_list.append(session_data)
    return session_data_list

async def updateSession(
    redis: redis.Redis,
    session_id: str,
    updated_data: dict
) -> None:
    
    session_data_raw = await redis.get(f"session:{session_id}")
    
    if session_data_raw:
        session_data = SessionData(**json.loads(session_data_raw))
        for key, value in updated_data.items():
            setattr(session_data, key, value)
        await redis.set(f"session:{session_id}", session_data.model_dump_json(), ex=3600)


async def deleteSession(
    redis: redis.Redis,
    session_id: str
) -> None:
    await redis.delete(f"session:{session_id}")

