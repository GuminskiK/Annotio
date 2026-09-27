from sqlmodel.ext.asyncio.session import AsyncSession
from models.Tasks import Task, TaskCreate, TaskUpdate
from sqlmodel import select
from app.core.exceptions import TaskAlreadyHaveAssignmentException, TaskNotFoundException
from uuid import UUID

async def create_task(session: AsyncSession, task: TaskCreate, owner_id: UUID):
    
    data = task.model_dump(exclude={"owner_id"})
    db_task = Task(**data)
    db_task.owner_id = owner_id
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)

    return db_task


async def fetch_task_by_id(session: AsyncSession, task_id: UUID, owner_id: UUID):

    result = await session.exec(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))
    task = result.one_or_none()

    if not task:
        raise TaskNotFoundException()

    return task


async def fetch_user_tasks(session: AsyncSession, owner_id: UUID):

    result = await session.exec(select(Task).where(Task.owner_id == owner_id))
    return result.all()

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

    return None