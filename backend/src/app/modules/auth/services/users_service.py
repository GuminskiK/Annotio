import shutil
from pathlib import Path as FilePath
from fastapi import BackgroundTasks, File, UploadFile
from sqlmodel import select
from utils.auth_utils import get_password_hash
from app.core.exceptions import (
    EmailTakenException,
    NoFileNameException,
    NoFileTypeException,
    UsernameTakenException,
    UserNotFoundException,
    WrongFileTypeException,
    NoFileException,
    InvalidTokenException,
    WrongTokenTypeException
)
from uuid import UUID, uuid4

from models.Users import User, UserCreate, UserUpdate
from models.Tokens import TokenTypes
from utils.users_utils import get_user_by_id, get_user_by_username, get_blind_index, get_user_by_email
from app.core.logger import get_logger
from models.CurrentUserContext import CurrentUserContext
from services.session_service import getSessionsByUserId, updateSession, deleteSession
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.jwt import create_token, decode_token
import redis.asyncio as redis
from datetime import datetime, timedelta, timezone
from services.email_service import send_activation_email, send_password_reset_email
from core.config import settings
from deps.dbs import db_session, redis_client

logger = get_logger(__name__)

async def create_user(
        session: AsyncSession,
        user: UserCreate,
        background_tasks: BackgroundTasks
):
    if await get_user_by_username(session, user.username):
        logger.warning("user_create_failed_username_taken")
        raise UsernameTakenException()

    if await get_user_by_email(session, user.email):
        logger.warning("user_create_failed_email_taken")
        raise EmailTakenException()
    
    hashed = get_password_hash(user.plain_password)

    user_data = user.model_dump(exclude={"plain_password"})
    email_blind_index = get_blind_index(user_data["email"])

    db_user = User(
        **user_data, hashed_password=hashed, email_blind_index=email_blind_index
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    logger.info("user_created_succesfully", user_id=db_user.id)

    if not db_user.id:
        logger.warning("user_create_failed_no_id")
        raise UserNotFoundException()
    token = create_token(db_user.id, db_user.username, TokenTypes.ACTIVATE, timedelta(days=settings.ACTIVATE_TOKEN_EXPIRE_DAYS))


    background_tasks.add_task(send_activation_email, db_user.email, token)

    return db_user

async def fetch_user_by_id(
    session: AsyncSession, 
    user_id: UUID
) -> User:
    
    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning("user_fetch_failed_not_found", user_id=user_id)
        raise UserNotFoundException()
    return user

async def fetch_all_users(session: AsyncSession) -> list[User]:
    result = await session.exec(select(User))
    users = list(result.all())
    return users

async def update_user(
    redis: redis.Redis,
    session: AsyncSession, 
    user_update: UserUpdate,
    user_id: UUID
) -> User:


    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning("user_update_failed_not_found", user_id=user_id)
        raise UserNotFoundException()
    
    if user_update.plain_password:
        hashed = get_password_hash(user_update.plain_password)
        user.hashed_password = hashed

    if user_update.email:
        existing_user = await get_user_by_email(session, user_update.email)

        if existing_user and existing_user.id != user_id:
            logger.warning(
                "user_patch_failed_email_taken",
                user_id=user_id,
            )
            raise EmailTakenException()

        user.email_blind_index = get_blind_index(user_update.email)


    update_data = user_update.model_dump(exclude_unset=True, exclude={"plain_password"})
    for key, value in update_data.items():
        setattr(user, key, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)

    session_ids = await getSessionsByUserId(redis, user.id)
    if not user_update.plain_password:
        for id in session_ids:
            await updateSession( redis, id, {"username": user.username})
    else:
        for id in session_ids:
            await deleteSession(redis, id)
            
    logger.info("user_updated_succesfully", user_id=user.id)
    
    return user

async def upload_avatar(
    redis: redis.Redis,
    session: AsyncSession,
    user: CurrentUserContext,
    file: UploadFile = File(...), 
):

    if file is None:
        raise NoFileException()
    
    if file.content_type is None:
        raise NoFileTypeException()
    
    if file.filename is None:
        raise NoFileNameException()

    if not file.content_type.startswith("image/"):
        raise WrongFileTypeException()

    AVATARS_DIR = FilePath("/app/static/avatars")
    AVATARS_DIR.mkdir(parents=True, exist_ok=True)

    file_extension = file.filename.split(".")[-1]
    new_filename = f"{uuid4()}.{file_extension}"
    file_path = AVATARS_DIR / new_filename

    contents = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    avatar_url = f"/static/avatars/{new_filename}"

    current_user = await get_user_by_id(session, user.user_id)
    if not current_user:
        logger.warning("user_avatar_upload_failed_not_found", user_id=user.user_id)
        raise UserNotFoundException()
    
    current_user.avatar_url = avatar_url
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    if current_user.id is None:
        logger.warning("user_avatar_upload_failed_not_found", user_id=user.user_id)
        raise UserNotFoundException()

    session_ids = await getSessionsByUserId(redis, current_user.id)
    for id in session_ids:
        await updateSession(redis, id, {"avatar_url": avatar_url})
        
    logger.info("user_avatar_uploaded_succesfully", user_id=user.user_id)
    return {"avatar_url": avatar_url}


async def change_user_role(    
    redis: redis.Redis,
    session: AsyncSession, 
    user_id: UUID, 
    is_superuser: bool,
):
    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning("user_change_role_failed_not_found", user_id=user_id)
        raise UserNotFoundException()
    
    user.is_superuser = is_superuser
    session.add(user)
    await session.commit()
    await session.refresh(user)

    if user.id is None:
        logger.warning("user_change_role_failed_not_found", user_id=user_id)
        raise UserNotFoundException()

    session_ids = await getSessionsByUserId(redis, user.id)
    for id in session_ids:
        await updateSession(redis, id, {"is_superuser": user.role == "admin"})

    logger.info("user_role_changed_succesfully", user_id=user.id, new_role="admin" if is_superuser else "user")

    return {"message": "User role changed successfully", "new_role": "admin" if is_superuser else "user"}
    

async def remove_user(session: AsyncSession, user_id: UUID):
    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning("user_remove_failed_not_found", user_id=user_id)
        raise UserNotFoundException()
    
    await session.delete(user)
    await session.commit()

    logger.info("user_removed_succesfully", user_id=user.id)

    return {"message": "User removed successfully"}

async def change_account_status(session: db_session, activate_token:str):

    try:
        payload = decode_token(activate_token)
    except Exception as e:
        logger.warning("token_decode_failed", error=str(e))
        raise InvalidTokenException()

    if payload.get("typ") != TokenTypes.ACTIVATE:
        logger.warning("wrong_token_type_presented", typ=payload.get("typ"))
        raise WrongTokenTypeException()

    jti = payload.get("jti")
    if not jti:
        logger.warning("token_missing_jti")
        raise InvalidTokenException()
    
    user_id = payload.get("id")
    if not user_id:
        logger.warning("token_missing_user_id")
        raise InvalidTokenException()
    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning("user_not_found")
        raise UserNotFoundException()

    user.is_activated = True
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    logger.info("account_activated", user_id=str(user.id))

    return user

async def send_change_password_mail(session: db_session, email: str, background_tasks: BackgroundTasks):

    user = await get_user_by_email(session, email)
    
    if not user:
        raise UserNotFoundException()

    token = create_token(
        user.id,
        user.username,
        TokenTypes.CHANGE_PASSWORD,
        timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        ),
    )
    background_tasks.add_task(send_password_reset_email, user.email, token)

    logger.info("password_change_mail_sent", user_id=str(user.id))

    return {"message": "success"}

async def change_password(session: db_session, password_change_token: str, plain_password: str):

    try:
        payload = decode_token(password_change_token)
    except Exception as e:
        logger.warning("token_decode_failed", error=str(e))
        raise InvalidTokenException()

    if payload.get("typ") != TokenTypes.CHANGE_PASSWORD:
        logger.warning("wrong_token_type_presented", typ=payload.get("typ"))
        raise WrongTokenTypeException()

    jti = payload.get("jti")
    if not jti:
        logger.warning("token_missing_jti")
        raise InvalidTokenException()
    
    user_id = payload.get("id")

    if not user_id:
        logger.warning("token_missing_user_id")
        raise InvalidTokenException()
    user = await get_user_by_id(session, user_id)
    if not user:
        logger.warning("user_not_found")
        raise UserNotFoundException()

    hashed = get_password_hash(plain_password)
    user.hashed_password = hashed

    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    logger.info("password_changed", user_id=str(user.id))

    return user