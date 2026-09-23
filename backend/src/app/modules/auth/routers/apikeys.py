from fastapi import APIRouter, Body
from uuid import UUID
from src.app.deps.users import CurrentUser, AdminUser
from services.apikeys_service import (
    fetch_user_apikeys,
    fetch_user_apikeys_by_id,
    generate_api_key_for_user,
    revoke_user_api_key
)
from app.deps.dbs import db_session, redis_client

router = APIRouter(prefix="/apikeys", tags=["apikeys"])

@router.post("", status_code=201)
async def post_apikey(user: CurrentUser, session: db_session, redis: redis_client, name: str = Body(..., embed=True)):

    return await generate_api_key_for_user(session, user.user_id, name, redis)


@router.delete("/{key_id}")
async def delete_api_key(key_id: UUID, user: CurrentUser, session: db_session, redis: redis_client):

    return await revoke_user_api_key(session, user.user_id, key_id, redis)


@router.get("/me")
async def get_my_keys(user: CurrentUser, session: db_session):
    return await fetch_user_apikeys(user, session)

@router.get("/{user_id}")
async def get_user_keys(user_id: UUID, admin: AdminUser, session: db_session):
    return await fetch_user_apikeys_by_id(user_id, session)