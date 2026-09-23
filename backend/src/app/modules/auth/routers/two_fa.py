from fastapi import APIRouter, Body

from app.deps.users import CurrentUser
from app.core.config import settings
from app.modules.auth.services.two_fa_service import (
    generate_setup_data,
    verify_and_disable,
    verify_and_enable,
)
from app.deps.dbs import db_session, redis_client

router = APIRouter(prefix="/2fa", tags=["2fa"])

APP_NAME = settings.APP_NAME


@router.post("/setup")
async def setup_2fa(user: CurrentUser, session: db_session):

    return await generate_setup_data(user, session)

@router.post("/enable")
async def enable_2fa(
    user: CurrentUser, 
    session: db_session, 
    redis: redis_client,
    code: str = Body(..., embed=True)
):
    return await verify_and_enable(user, redis, session, code)

@router.post("/disable")
async def disable_2fa(
    user: CurrentUser,
    session: db_session,
    redis: redis_client,
    code: str = Body(..., embed=True)
):

    return await verify_and_disable(user, redis, session, code)
