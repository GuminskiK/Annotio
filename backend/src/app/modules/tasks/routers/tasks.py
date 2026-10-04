from uuid import UUID

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile
from src.app.deps.dbs import db_session
from src.app.deps.users import CurrentUser
from src.app.modules.tasks.models.Tasks import (
    TaskAnswerType,
    TaskContentType,
    TaskCreate,
    TaskPage,
    TaskRead,
    TaskUpdate,
)
from src.app.modules.tasks.models.ResourceFile import ResourceFileRead
from src.app.modules.tasks.services.task_crud import (
    create_task,
    delete_task,
    fetch_task_by_id,
    fetch_user_tasks,
    list_tasks,
    upload_task_files,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead, status_code=201)
async def post_task(session: db_session, user: CurrentUser, task: TaskCreate):
    return await create_task(session, task, user.user_id)


@router.get("", response_model=TaskPage)
async def get_tasks(
    session: db_session,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    reward_min: Decimal | None = None,
    reward_max: Decimal | None = None,
    time_limit_min: int | None = Query(None, ge=1),
    time_limit_max: int | None = Query(None, ge=1),
    reward_order: str | None = Query(None, pattern="^(asc|desc)$"),
    time_order: str | None = Query(None, pattern="^(asc|desc)$"),
    task_content_type: TaskContentType | None = None,
    task_answer_type: TaskAnswerType | None = None,
    owner_id: UUID | None = None,
    campaign_id: UUID | None = None,
):
    return await list_tasks(
        session=session,
        page=page,
        page_size=page_size,
        reward_min=reward_min,
        reward_max=reward_max,
        time_limit_min=time_limit_min,
        time_limit_max=time_limit_max,
        reward_order=reward_order,
        time_order=time_order,
        content_type=task_content_type,
        answer_type=task_answer_type,
        owner_id=owner_id,
        campaign_id=campaign_id,
    )

@router.get("/users/{user_id}", response_model=list[TaskRead])
async def get_tasks_by_user_id(session: db_session, user_id: UUID):
    return await fetch_user_tasks(session, user_id)


@router.post("/{task_id}/files", response_model=list[ResourceFileRead])
async def post_task_files(
    session: db_session,
    user: CurrentUser,
    task_id: UUID,
    files: list[UploadFile] = File(...),
):
    return await upload_task_files(session, task_id, user.user_id, files)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(session: db_session, task_id: UUID, user: CurrentUser):
    return await fetch_task_by_id(session, task_id, user.user_id)

@router.patch("/{task_id}", response_model=TaskRead)
async def patch_task(session: db_session, user: CurrentUser, task_id: UUID, update: TaskUpdate):
    return await update_task(session, update, task_id, user.user_id)

@router.delete("/{task_id}", status_code=204)
async def remove_task(session: db_session, user: CurrentUser, task_id: UUID):
    return await delete_task(session, task_id, user.user_id)