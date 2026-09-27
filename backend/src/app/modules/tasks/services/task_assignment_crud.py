from sqlmodel.ext.asyncio.session import AsyncSession
from models.TaskAssignments import TaskAssignment
from sqlmodel import select
from app.core.exceptions import TaskAssignmentNotFoundException
from uuid import UUID


async def fetch_task_assignment_by_id(session: AsyncSession, task_assignment_id: UUID):

    result = await session.exec(select(TaskAssignment).where(TaskAssignment.id == task_assignment_id))
    task_assignment = result.one_or_none()

    if not task_assignment:
        raise TaskAssignmentNotFoundException()

    return task_assignment


async def fetch_user_task_assignments(session: AsyncSession, worker_id: UUID):

    result = await session.exec(select(TaskAssignment).where(TaskAssignment.worker_id == worker_id))
    return result.all()