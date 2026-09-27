from typing import List
from uuid import UUID

from fastapi import APIRouter

from src.app.deps.dbs import db_session
from src.app.deps.users import CurrentUser
from src.app.modules.tasks.models.Tasks import TaskCreate, TaskRead, TaskUpdate
from src.app.modules.tasks.services.task_crud import (
    create_task,
    delete_task,
    fetch_task_by_id,
    fetch_user_tasks,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead, status_code=201)
async def post_task(session: db_session, user: CurrentUser, task: TaskCreate):
    return await create_task(session, task, user.user_id)

@router.get("/users/{user_id}", response_model=List[TaskRead])
async def get_tasks(session: db_session, user_id: UUID):
    return await fetch_user_tasks(session, user_id)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(session: db_session, task_id: UUID, user: CurrentUser):
    return await fetch_task_by_id(session, task_id, user.user_id)

@router.patch("/{task_id}", response_model=TaskRead)
async def patch_task(session: db_session, user: CurrentUser, task_id: UUID, update: TaskUpdate):
    return await update_task(session, update, task_id, user.user_id)

@router.delete("/{task_id}", status_code=204)
async def remove_task(session: db_session, user: CurrentUser, task_id: UUID):
    return await delete_task(session, task_id, user.user_id)