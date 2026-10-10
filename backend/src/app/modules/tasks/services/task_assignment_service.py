from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.exceptions import (
    TaskAlreadyReservedException,
    TaskAssignmentNotFoundException,
    TaskNotFoundException,
)
from src.app.modules.tasks.models.TaskAssignments import (
    TaskAssignment,
    TaskAssignmentStatus,
)
from src.app.modules.tasks.models.Tasks import Task
from src.app.modules.tasks.models.ResourceFile import ResourceFile
from src.app.modules.tasks.models.TaskViews import TaskAssignmentView, TaskResourceView

active_statuses = (
    TaskAssignmentStatus.RESERVED,
    TaskAssignmentStatus.SUBMITTED,
    TaskAssignmentStatus.ACCEPTED,
)

async def reserve_task(
    session: AsyncSession,
    task_id: UUID,
    worker_id: UUID,
) -> TaskAssignment:
    
    task_result = await session.exec(
        select(Task)
        .where(Task.id == task_id)
        .with_for_update()
    )

    task = task_result.one_or_none()

    if task is None:
        raise TaskNotFoundException()


    count_result = await session.exec(
        select(func.count())
        .select_from(TaskAssignment)
        .where(
            TaskAssignment.task_id == task_id,
            cast(Any, TaskAssignment.status).in_(active_statuses),
            TaskAssignment.expires_at > func.now()
        )
    )
    active_count = count_result.one()

    if active_count >= task.required_assignments:
        raise TaskAlreadyReservedException()

    assignment = TaskAssignment(
        task_id=task_id,
        worker_id=worker_id,
        status=TaskAssignmentStatus.RESERVED,
        reserved_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=task.time_limit_minutes),
    )

    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)

    return assignment

async def fetch_task_assignment_by_token(
    session: AsyncSession,
    token: str,
    user_id: UUID
) -> TaskAssignment:
    result = await session.exec(
        select(TaskAssignment)
        .where(
            TaskAssignment.token == token,
            TaskAssignment.worker_id == user_id,
            TaskAssignment.expires_at > func.now()
        )
    )
    assignment = result.one_or_none()
    if assignment is None:
        raise TaskAssignmentNotFoundException()
    return assignment

async def submit_task_assignment(
    session: AsyncSession,
    token: str,
    user_id: UUID,
    result_data_json: dict
) -> TaskAssignment:
    assignment = await fetch_task_assignment_by_token(session, token, user_id)

    if assignment.status != TaskAssignmentStatus.RESERVED:
        raise TaskNotFoundException()

    assignment.status = TaskAssignmentStatus.SUBMITTED
    assignment.result_data_json = result_data_json
    assignment.submitted_at = datetime.now(timezone.utc)

    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)

    return assignment

async def change_status(
    session: AsyncSession,
    assignment_id: UUID,
    old_status: TaskAssignmentStatus,
    new_status: TaskAssignmentStatus
) -> TaskAssignment:
    result = await session.exec(
        select(TaskAssignment)
        .where(TaskAssignment.id == assignment_id)
        .with_for_update()
    )
    assignment = result.one_or_none()

    if assignment is None:
        raise TaskAssignmentNotFoundException()

    if assignment.status != old_status:
        raise TaskNotFoundException()

    assignment.status = new_status

    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)

    return assignment


async def fetch_task_assignment_view(
    session: AsyncSession,
    assignment_id: UUID,
    user_id: UUID | None,
    resource_id: UUID | None = None,
):
    conditions = [TaskAssignment.id == assignment_id]
    if user_id is not None:
        conditions.append(TaskAssignment.worker_id == user_id)
    assignment_result = await session.exec(select(TaskAssignment).where(*conditions))
    assignment = assignment_result.one_or_none()
    if assignment is None:
        raise TaskAssignmentNotFoundException()

    task_result = await session.exec(select(Task).where(Task.id == assignment.task_id))
    task = task_result.one_or_none()
    if task is None:
        raise TaskNotFoundException()

    resources_result = await session.exec(
        select(ResourceFile).where(ResourceFile.task_id == task.id)
    )
    resources = list(resources_result.all())
    if resource_id is not None:
        resource = next((item for item in resources if item.id == resource_id), None)
        return resource.storage_path if resource else None

    return TaskAssignmentView(
        assignment_id=assignment.id,
        task_id=task.id,
        status=assignment.status,
        expires_at=assignment.expires_at,
        task_content_type=task.task_content_type,
        task_answer_type=task.task_answer_type,
        data_json=task.data_json,
        resource_files=[
            TaskResourceView(
                id=resource.id,
                original_name=resource.original_name,
                url=f"/api/task_assignments/{assignment.id}/files/{resource.id}",
            )
            for resource in resources
        ],
        result_data_json=assignment.result_data_json,
    )