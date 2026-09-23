from fastapi import Depends, Form, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
import redis.asyncio as redis
from app.modules.auth.utils.auth_utils import verify_password
from app.modules.auth.utils.users_utils import get_user_by_username, get_user_by_id
from app.core.exceptions import (
    InvalidCredentialsException,
    Required2FACodeException,
    Invalid2FACodeException,
    TwoFaSecretMissingException,
    UserNotFoundException
)
import asyncio
import pyotp
from app.core.config import settings
from core.logger import get_logger
from app.modules.auth.services.session_service import createSession
import secrets
from uuid import UUID
logger = get_logger(__name__)

async def login(
    request: Request,
    response: Response,
    redis: redis.Redis,
    session: AsyncSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):

    await asyncio.sleep(1)

    user = await get_user_by_username(session, form_data.username)
    if not user:
        verify_password(form_data.password, settings.DUMMY_HASH)
        logger.warning("invalid_user_login_attempt", username=form_data.username)
        raise InvalidCredentialsException()

    if not verify_password(form_data.password, user.hashed_password):
        logger.warning("invalid_credentials_attempt", username=form_data.username)
        raise InvalidCredentialsException()


    if user.is_totp_enabled:

        mfa_token = secrets.token_urlsafe(32)

        await redis.setex(f"mfa_pending:{mfa_token}", 300, str(user.id))

        logger.info("2fa_required_for_login", user_id=str(user.id))

        response.status_code = status.HTTP_202_ACCEPTED

        return {
            "status": "mfa_required", 
            "mfa_token": mfa_token,
            "message": "Podaj kod 2FA"
        }

    await createSession(request, response, user, redis)

    logger.info("user_logged_in", user_id=str(user.id), uuid=str(user.id))

    return {"message": "Logged in successfully!"}


async def login_mfa(
    request: Request,
    response: Response,
    redis: redis.Redis,
    session: AsyncSession,
    mfa_token: str,
    mfa_code: str,     
):
    user_id = await redis.get(f"mfa_pending:{mfa_token}")
    if not user_id:
        raise InvalidCredentialsException(detail="Sesja 2FA wygasła lub jest nieprawidłowa")

    user_id_str = user_id.decode("utf-8") if isinstance(user_id, bytes) else user_id

    user = await get_user_by_id(session, UUID(user_id_str))

    if not user:
        logger.warning("user_not_found", user_id = user_id)
        raise UserNotFoundException()

    if not mfa_code:
        logger.info("2fa_code_missing", username=user.username)
        raise Required2FACodeException()

    if user.totp_secret is None:
        logger.warning("2fa_secret_missing", username=user.username)
        raise TwoFaSecretMissingException()
    
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(mfa_code):
        logger.warning("invalid_2fa_code_attempt", username=user.username)
        raise Invalid2FACodeException()

    await createSession(request, response, user, redis)

    logger.info("user_logged_in", user_id=str(user.id), uuid=str(user.id))

    return {"message": "Logged in successfully!"}

    
async def logout(request: Request, response: Response, redis: redis.Redis):
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if session_id:
        await redis.delete(f"session:{session_id}")
    response.delete_cookie(settings.SESSION_COOKIE_NAME)

    logger.info("user_logged_out", session_id=str(session_id))

    return {"message": "Wylogowano pomyślnie, sesja zniszczona"}