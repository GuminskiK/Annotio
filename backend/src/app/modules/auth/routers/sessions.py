from uuid import UUID

from fastapi import APIRouter
from src.app.core.exceptions import CurrentUserNeededException
from src.app.deps.dbs import redis_client
from src.app.deps.users import AdminUser, CurrentUser
from src.app.modules.auth.models.Users import Role
from src.app.modules.auth.services.session_service import (
    deleteSession,
    getSessionDataByUserId,
    getSessionsByUserId,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/me")
async def get_sessions_me (user: CurrentUser, redis: redis_client):

    return await getSessionDataByUserId(redis, user.user_id)

@router.get("/{user_id}")
async def get_sessions_by_user_id (user_id: UUID, admin: AdminUser, redis: redis_client):

    return await getSessionDataByUserId(redis, user_id)

@router.delete("/{session_id}")
async def delete_session_by_id (user: CurrentUser, session_id: str, redis: redis_client):

    if ( session_id not in await getSessionsByUserId(redis, user.user_id) and not user.role == Role.ADMIN):
        raise CurrentUserNeededException(detail="You can only delete your own sessions unless you are an admin")

    return await deleteSession( redis, session_id)