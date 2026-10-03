from fastapi import APIRouter, Body, Depends, Form, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from src.app.deps.dbs import db_session, redis_client
from src.app.modules.auth.services.auth_service import login, login_mfa, logout

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login_route(    
    request: Request,
    response: Response,
    redis: redis_client,
    session: db_session,
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = Form(False),
    ):
    
    login_response = await login(
        request=request,
        response=response,
        redis=redis,
        session=session,
        form_data=form_data,
        remember_me=remember_me,
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
    remember_me: bool = Body(False),
):
    login_mfa_response = await login_mfa(        
        request=request,
        response=response,
        redis=redis,
        session=session,
        mfa_token=mfa_token,
        mfa_code=mfa_code,
        remember_me=remember_me,
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