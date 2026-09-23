import hashlib
import json
from typing import Optional
from fastapi.security import APIKeyHeader
from fastapi import Depends, HTTPException, status, Request, Response
from core.exceptions import (
    AdminNeededException, CurrentUserNeededException, NoSessionAndNoAPIKey
)
from app.modules.auth.models.SessionData import SessionData
from app.modules.auth.models.CurrentUserContext import CurrentUserContext
import redis.asyncio as redis
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID


from backend.src.app.deps.users import AuthDependency, CurrentUserContext
from app.core.config import settings
from dbs import redis_pure, db_deps
from src.app.modules.auth.models.Users import User
from fastapi import Depends
from typing import Annotated
from backend.src.app.deps.users import CurrentUserContext

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

class AuthDependency:
    def __init__(self, session_cookie_name: str, session_ttl: int, redis: redis.Redis, db_session: AsyncSession):
        self.session_cookie_name = session_cookie_name
        self.SESSION_TTL = session_ttl
        self.redis = redis

    async def get_current_session(
        self, 
        request: Request, 
        response: Response,
        api_key: Optional[str] = Depends(api_key_header)
    ) -> CurrentUserContext:
    
        session_id = request.cookies.get(self.session_cookie_name)
        if session_id:
            redis_key = f"session:{session_id}"
            session_raw = await self.redis.get(redis_key)
            
            if not session_raw:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesja wygasła lub nie istnieje")
            
            session_data = SessionData(**json.loads(session_raw))
            
            await self.redis.expire(redis_key, self.SESSION_TTL)
            
            response.set_cookie(
                key=self.session_cookie_name,
                value=session_id,
                max_age=self.SESSION_TTL,
                httponly=True,
                secure=False,
                samesite="lax"
            )

            return CurrentUserContext(
                    session_id=session_data.session_id,

                    user_id=session_data.user_id,
                    username=session_data.username,
                    is_superuser=session_data.is_superuser,
                    is_totp_enabled=session_data.is_totp_enabled,

                    avatar_url=session_data.avatar_url
            )
        
        if api_key:
            hashed_key = _hash_api_key(api_key)
            redis_cache_key = f"apikey:{hashed_key}"
            
            cached_key_data = await self.redis.get(redis_cache_key)
            if cached_key_data:
                key_data = json.loads(cached_key_data)
                return CurrentUserContext(
                    session_id=key_data["session_id"],

                    user_id=key_data["id"],
                    username=key_data["username"],
                    is_superuser=key_data["is_superuser"],
                    is_totp_enabled=key_data["is_totp_enabled"],

                    avatar_url=key_data["avatar_url"]
                )

        raise NoSessionAndNoAPIKey()
    
    def get_current_admin_session(self):
        async def _get_current_admin_user(
            current_user: CurrentUserContext = Depends(self.get_current_session)
        ) -> CurrentUserContext:
            if not current_user.is_superuser:
                raise AdminNeededException()
            return current_user
        return _get_current_admin_user


session = db_deps.AsyncSessionLocal()

auth_dependency = AuthDependency(
    session_cookie_name=settings.SESSION_COOKIE_NAME,
    session_ttl=settings.SESSION_TTL,
    redis=redis_pure,
    db_session=session
)

CurrentUser = Annotated[CurrentUserContext, Depends(auth_dependency.get_current_session)]
AdminUser = Annotated[CurrentUserContext, Depends(auth_dependency.get_current_admin_session())]