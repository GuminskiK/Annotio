from uuid import UUID
from decimal import Decimal
from typing import Any, cast
from fastapi import UploadFile

from sqlalchemy import asc, desc
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.exceptions import (
    TaskAlreadyHaveAssignmentException,
    TaskNotFoundException,
)
from src.app.modules.tasks.models.Tasks import (
    Task,
    TaskContentType,
    TaskAnswerType,
    TaskCreate,
    TaskPage,
    TaskRead,
    TaskUpdate,
)
from src.app.core.storage import object_storage
from src.app.modules.tasks.models.ResourceFile import ResourceFile


async def create_task(session: AsyncSession, task: TaskCreate, owner_id: UUID):
    
    data = task.model_dump(exclude={"owner_id"})
    db_task = Task(**data)
    db_task.owner_id = owner_id
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)

    return db_task


async def upload_task_files(
    session: AsyncSession,
    task_id: UUID,
    owner_id: UUID,
    files: list[UploadFile],
) -> list[ResourceFile]:
    result = await session.exec(
        select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
    )
    task = result.one_or_none()
    if task is None:
        raise TaskNotFoundException()

    if task.task_content_type == TaskContentType.TEXT:
        raise ValueError("Text tasks do not accept resource files")

    resources: list[ResourceFile] = []
    for file in files:
        content_type = file.content_type or "application/octet-stream"
        expected_prefix = "image/" if task.task_content_type == TaskContentType.IMAGE else "video/"
        if not content_type.startswith(expected_prefix):
            raise ValueError(f"Expected {expected_prefix} files for this task")
        if not file.filename:
            continue
        object_name = await object_storage.upload(
            await file.read(), file.filename, content_type
        )
        resources.append(
            ResourceFile(
                task_id=task_id,
                storage_path=object_name,
                original_name=file.filename,
            )
        )

    session.add_all(resources)
    await session.commit()
    for resource in resources:
        await session.refresh(resource)
    return resources


async def fetch_task_by_id(session: AsyncSession, task_id: UUID, owner_id: UUID):

    result = await session.exec(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))
    task = result.one_or_none()

    if not task:
        raise TaskNotFoundException()

    return task


async def fetch_user_tasks(session: AsyncSession, owner_id: UUID):

    result = await session.exec(select(Task).where(Task.owner_id == owner_id))
    return result.all()


async def list_tasks(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    reward_min: Decimal | None = None,
    reward_max: Decimal | None = None,
    time_limit_min: int | None = None,
    time_limit_max: int | None = None,
    reward_order: str | None = None,
    time_order: str | None = None,
    content_type: TaskContentType | None = None,
    answer_type: TaskAnswerType | None = None,
    owner_id: UUID | None = None,
    campaign_id: UUID | None = None,
) -> TaskPage:
    filters = []
    if reward_min is not None:
        filters.append(Task.reward >= reward_min)
    if reward_max is not None:
        filters.append(Task.reward <= reward_max)
    if time_limit_min is not None:
        filters.append(Task.time_limit_minutes >= time_limit_min)
    if time_limit_max is not None:
        filters.append(Task.time_limit_minutes <= time_limit_max)
    if content_type is not None:
        filters.append(Task.task_content_type == content_type)
    if answer_type is not None:
        filters.append(Task.task_answer_type == answer_type)
    if owner_id is not None:
        filters.append(Task.owner_id == owner_id)
    if campaign_id is not None:
        filters.append(Task.campaign_id == campaign_id)

    count_result = await session.exec(
        select(func.count()).select_from(Task).where(*filters)
    )
    total = count_result.one()

    order_by = []
    if reward_order == "asc":
        order_by.append(asc(cast(Any, Task.reward)))
    elif reward_order == "desc":
        order_by.append(desc(cast(Any, Task.reward)))
    if time_order == "asc":
        order_by.append(asc(cast(Any, Task.time_limit_minutes)))
    elif time_order == "desc":
        order_by.append(desc(cast(Any, Task.time_limit_minutes)))
    if not order_by:
        order_by.append(Task.id)

    offset = (page - 1) * page_size
    result = await session.exec(
        select(Task).where(*filters).order_by(*order_by).offset(offset).limit(page_size)
    )
    pages = (total + page_size - 1) // page_size if total else 0
    return TaskPage(
        items=cast(list[TaskRead], list(result.all())),
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )

async def update_task(session: AsyncSession, task_update: TaskUpdate, task_id: UUID, owner_id: UUID):

    result = await session.exec(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))
    db_task = result.one_or_none()

    if not db_task:
        raise TaskNotFoundException()

    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)

    return db_task


async def delete_task(session: AsyncSession, task_id: UUID, owner_id: UUID):

    result = await session.exec(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))
    db_task = result.one_or_none()

    if not db_task:
        raise TaskNotFoundException()

    if db_task.assignments:
        raise TaskAlreadyHaveAssignmentException()

    await session.delete(db_task)
    await session.commit()

