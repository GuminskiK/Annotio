from fastapi import APIRouter
from app.modules.auth.services.session_service import (
    getSessionDataByUserId,
    getSessionsByUserId,
    deleteSession
)
from app.core.exceptions import CurrentUserNeededException
from app.deps.users import CurrentUser, AdminUser
from app.deps.dbs import redis_client
from uuid import UUID

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/me")
async def get_sessions_me (user: CurrentUser, redis: redis_client):

    return await getSessionDataByUserId(redis, user.user_id)

@router.get("/{user_id}")
async def get_sessions_by_user_id (user_id: UUID, admin: AdminUser, redis: redis_client):

    return await getSessionDataByUserId(redis, user_id)

@router.delete("/{session_id}")
async def delete_session_by_id (user: CurrentUser, session_id: str, redis: redis_client):

    if ( session_id not in await getSessionsByUserId(redis, user.user_id) and not user.is_superuser):
        raise CurrentUserNeededException(detail="You can only delete your own sessions unless you are an admin")

    return await deleteSession( redis, session_id)