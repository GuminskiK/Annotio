import pyotp

from app.core.config import settings
from app.core.exceptions import (
    Invalid2FACodeException,
    TwoFaAlreadyEnabledException,
    TwoFaNotEnabledException,
    TwoFaNotInitiatedException,
    TwoFaSecretMissingException,
    UserNotFoundException,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from services.session_service import getSessionsByUserId, updateSession
from core.logger import get_logger
from deps.users import CurrentUserContext
from utils.users_utils import get_user_by_id
import redis.asyncio as redis

logger = get_logger(__name__)


async def generate_setup_data(user_context: CurrentUserContext, session: AsyncSession):
    
    user = await get_user_by_id(session, user_context.user_id)
    
    if not user:
        logger.error("user_not_found", user_id=str(user_context.user_id))
        raise UserNotFoundException()

    if user.is_totp_enabled:
        logger.info("2fa_setup_already_enabled", user_id=str(user.id))
        raise TwoFaAlreadyEnabledException()

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user.username, issuer_name=settings.APP_NAME
    )

    user.totp_secret = secret
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {
            "secret": user.totp_secret,
            "qr_code_uri": provisioning_uri
        }


async def verify_and_enable(user_context: CurrentUserContext, redis: redis.Redis, session: AsyncSession, code: str):

    user = await get_user_by_id(session, user_context.user_id)

    if not user:
        logger.error("user_not_found", user_id=str(user_context.user_id))
        raise UserNotFoundException()

    if user.is_totp_enabled:
        raise TwoFaAlreadyEnabledException()

    if not user.totp_secret:
        raise TwoFaNotInitiatedException()

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(code):
        raise Invalid2FACodeException()

    user.is_totp_enabled = True
    session.add(user)
    await session.commit()

    session_ids = await getSessionsByUserId(redis, user_context.user_id)
    for id in session_ids:
        await updateSession(redis, id, {"is_totp_enabled": True})

    logger.info("2fa_enabled", user_id=str(user.id))

    return {"message": "2FA successfully enabled"}


async def verify_and_disable(user_context: CurrentUserContext, redis: redis.Redis, session: AsyncSession, code: str):

    user = await get_user_by_id(session, user_context.user_id)

    if not user:
        logger.error("user_not_found", user_id=str(user_context.user_id))
        raise UserNotFoundException()

    if not user.is_totp_enabled:
        raise TwoFaNotEnabledException()

    if not user.totp_secret:
        raise TwoFaSecretMissingException()

    totp = pyotp.TOTP(user.totp_secret)

    if not totp.verify(code):
        raise Invalid2FACodeException()

    user.is_totp_enabled = False
    user.totp_secret = None
    session.add(user)
    await session.commit()

    session_ids = await getSessionsByUserId(redis, user_context.user_id)
    for id in session_ids:
        await updateSession(redis, id, {"is_totp_enabled": False})

    logger.info("2fa_disabled", user_id=str(user.id))

    return {"message": "2FA successfully disabled"}
