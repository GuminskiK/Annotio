
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, File, Response, UploadFile
from src.app.deps.dbs import db_session, redis_client
from src.app.deps.users import AdminUser, CurrentUser
from src.app.modules.auth.models.CurrentUserContext import CurrentUserContext
from src.app.modules.auth.models.Users import (
    NewPasswordModel,
    UserCreate,
    UserAccessUpdate,
    UserRead,
    UserUpdate,
)
from src.app.modules.auth.services.users_service import (
    change_account_status,
    change_password,
    change_user_role,
    create_user,
    fetch_all_users,
    fetch_user_by_id,
    remove_user,
    send_change_password_mail,
    update_user,
    update_user_access,
    upload_avatar,
)
from src.app.core.storage import object_storage
from fastapi.responses import Response as FileResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def post_user(
    session: db_session, user: UserCreate, background_tasks: BackgroundTasks
):

    return await create_user(session, user, background_tasks)

@router.get("", response_model=list[UserRead])
async def get_all_users(session: db_session, admin: AdminUser):

    return await fetch_all_users(session)

@router.get("/me", response_model=CurrentUserContext)
async def get_current_user( current_user: CurrentUser):
    return current_user


@router.post("/forgot_password")
async def forgot_password(
    session: db_session,
    background_tasks: BackgroundTasks,
    email: str = Body(..., embed=True),
):
    await send_change_password_mail(session, email, background_tasks)
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.patch("/change_password/{password_change_token}")
async def patch_password(
    session: db_session,
    password_change_token: str,
    payload: NewPasswordModel,
):
    await change_password(session, password_change_token, payload.plain_password)
    return {"message": "Password has been successfully changed."}

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


@router.patch("/{user_id}/roles", response_model=UserRead)
async def add_user_role(
    redis: redis_client,
    session: db_session,
    user_id: UUID,
    access: UserAccessUpdate,
    admin: AdminUser,
):
    return await update_user_access(redis, session, user_id, access)


@router.patch("/me/access", response_model=UserRead)
async def patch_user_access(
    redis: redis_client,
    session: db_session,
    current_user: CurrentUser,
    access: UserAccessUpdate,
    admin: AdminUser,
):
    return await update_user_access(redis, session, current_user.user_id, access)

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


@router.get("/me/avatar")
async def get_current_user_avatar(session: db_session, user: CurrentUser):
    current_user = await fetch_user_by_id(session, user.user_id)
    if not current_user.avatar_url:
        return Response(status_code=404)
    data, content_type = await object_storage.download(current_user.avatar_url)
    return FileResponse(content=data, media_type=content_type)

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
