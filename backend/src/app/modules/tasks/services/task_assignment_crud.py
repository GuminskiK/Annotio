from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.exceptions import TaskAssignmentNotFoundException
from src.app.modules.tasks.models.TaskAssignments import TaskAssignment


async def fetch_task_assignment_by_id(session: AsyncSession, task_assignment_id: UUID):

    result = await session.exec(select(TaskAssignment).where(TaskAssignment.id == task_assignment_id))
    task_assignment = result.one_or_none()

    if not task_assignment:
        raise TaskAssignmentNotFoundException()

    return task_assignment


async def fetch_user_task_assignments(session: AsyncSession, worker_id: UUID):

    result = await session.exec(select(TaskAssignment).where(TaskAssignment.worker_id == worker_id))
    return result.all()