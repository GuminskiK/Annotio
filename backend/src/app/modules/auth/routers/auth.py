from fastapi import APIRouter, Depends, Body, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from app.deps.dbs import db_session, redis_client
from app.modules.auth.services.auth_service import login, logout, login_mfa

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login_route(    
    request: Request,
    response: Response,
    redis: redis_client,
    session: db_session,
    form_data: OAuth2PasswordRequestForm = Depends(),
    ):
    
    login_response = await login(
        request=request,
        response=response,
        redis=redis,
        session=session,
        form_data=form_data
    )
    
    return login_response

@router.post("/login/mfa")
async def login_mfa_route(
    request: Request,
    response: Response,
    redis: redis_client,
    session: db_session,
    mfa_token: str = Body(...),
    mfa_code: str = Body(...),
):
    login_mfa_response = await login_mfa(        
        request=request,
        response=response,
        redis=redis,
        session=session,
        mfa_token=mfa_token,
        mfa_code=mfa_code
    )

    return login_mfa_response

@router.post("/logout")
async def logout_route(
    request: Request, 
    response: Response, 
    redis: redis_client):

    logout_response = await logout(
        request=request, 
        response=response, 
        redis=redis
    )

    return logout_response