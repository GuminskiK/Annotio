from uuid import UUID

from backend.src.app.modules.tasks.services.task_assignment_service import change_status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.modules.tasks.models.TaskAssignments import (
    TaskAssignment,
    TaskAssignmentStatus,
)


async def accept_task_assignment(
    session: AsyncSession,
    assignment_id: UUID,
) -> TaskAssignment:

    assignment = await change_status(
        session=session,
        assignment_id=assignment_id,
        old_status=TaskAssignmentStatus.SUBMITTED,
        new_status=TaskAssignmentStatus.ACCEPTED
    )

    return assignment

async def reject_task_assignment(
    session: AsyncSession,
    assignment_id: UUID,
) -> TaskAssignment:

    assignment = await change_status(
        session=session,
        assignment_id=assignment_id,
        old_status=TaskAssignmentStatus.SUBMITTED,
        new_status=TaskAssignmentStatus.REJECTED
    )

    return assignment

async def dispute_rejection(
    session: AsyncSession,
    assignment_id: UUID,
) -> TaskAssignment:

    assignment = await change_status(
        session=session,
        assignment_id=assignment_id,
        old_status=TaskAssignmentStatus.REJECTED,
        new_status=TaskAssignmentStatus.SUBMITTED
    )

    return assignment

async def auditor_won_dispute(
    session: AsyncSession,
    assignment_id: UUID,
) -> TaskAssignment:

    assignment = await change_status(
        session=session,
        assignment_id=assignment_id,
        old_status=TaskAssignmentStatus.SUBMITTED,
        new_status=TaskAssignmentStatus.REJECTED
    )

    return assignment


async def worker_won_dispute(
    session: AsyncSession,
    assignment_id: UUID,
) -> TaskAssignment:

    assignment = await change_status(
        session=session,
        assignment_id=assignment_id,
        old_status=TaskAssignmentStatus.SUBMITTED,
        new_status=TaskAssignmentStatus.ACCEPTED
    )

    return assignment