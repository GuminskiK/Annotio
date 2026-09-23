from typing import List

from fastapi import APIRouter, Depends, Body, Request, Response
from models.CurrentUserContext import CurrentUserContext
from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from uuid import UUID
from app.deps.users import CurrentUser, AdminUser
from app.modules.auth.models.Users import NewPasswordModel, UserCreate, UserRead, UserUpdate
from app.modules.auth.services.users_service import (
    change_account_status,
    change_password,
    create_user,
    fetch_all_users,
    fetch_user_by_id,
    remove_user,
    send_change_password_mail,
    update_user,
    upload_avatar,
    change_user_role
)
from app.deps.dbs import db_session, redis_client

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def post_user(
    session: db_session, user: UserCreate, admin: AdminUser, background_tasks: BackgroundTasks
):

    return await create_user(session, user, background_tasks)

@router.get("", response_model=List[UserRead])
async def get_all_users(session: db_session, admin: AdminUser):

    return await fetch_all_users(session)

@router.get("/me", response_model=CurrentUserContext)
async def get_current_user( current_user: CurrentUser):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
async def get_user(session: db_session, user_id: UUID, admin: AdminUser):

    return await fetch_user_by_id(session, user_id)


@router.patch("/me", response_model=UserRead)
async def patch_user(
    redis: redis_client,
    session: db_session, 
    user: UserUpdate, 
    current_user: CurrentUser,
):

    return await update_user(redis, session, user, current_user.user_id)

@router.patch("/{user_id}", response_model=UserRead)
async def patch_user_admin(
    redis: redis_client,
    session: db_session, 
    user: UserUpdate, 
    admin: AdminUser,
    user_id: UUID,
):

    return await update_user(redis, session, user, user_id)

@router.delete("/me", response_model=UserRead)
async def delete_user(session: db_session, user: CurrentUser):

    return await remove_user(session, user.user_id)

@router.delete("/{user_id}", response_model=UserRead)
async def delete_user_admin(
    session: db_session, user_id: UUID, admin: AdminUser
):

    return await remove_user(session, user_id)

@router.post("/me/avatar")
async def upload_avatar_route(
    redis: redis_client,
    session: db_session,
    user: CurrentUser,
    file: UploadFile = File(...), 
):
   
    result = await upload_avatar(redis, session, user, file)
    return result

@router.patch("/change_role/{user_id}")
async def patch_change_user_role(
    redis: redis_client,
    session: db_session, 
    user_id: UUID, 
    is_superuser: bool,
    admin: AdminUser
):
    result = await change_user_role(redis, session, user_id, is_superuser)
    return result

@router.patch("/activate/{activate_token}", response_model=UserRead)
async def activate_account(session: db_session, activate_token: str):

    return await change_account_status(session, activate_token)

@router.post("/forgot_password")
async def forgot_password(session: db_session, background_tasks: BackgroundTasks, email: str = Body(..., embed=True)):

    await send_change_password_mail(session, email, background_tasks)

    return {"message": "Jeśli to konto instnieje, wysłaliśmy instrukcje resetu hasła na wskazany adres e-mail."}

@router.patch("/change_password/{password_change_token}")
async def patch_password(session: db_session, password_change_token: str, payload: NewPasswordModel):

    await change_password(session, password_change_token, payload.plain_password)

    return {"message": "Hasło zostało pomyślnie zmienione."}