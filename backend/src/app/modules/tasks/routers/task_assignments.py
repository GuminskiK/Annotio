from typing import List
from uuid import UUID

from fastapi import APIRouter

from src.app.deps.dbs import db_session
from src.app.deps.users import CurrentUser
from src.app.modules.tasks.models.TaskAssignments import TaskAssignmentCreate, TaskAssignmentRead, TaskAssignmentUpdate
from src.app.modules.tasks.services.task_assignment_crud import (
    fetch_task_assignment_by_id,
    fetch_user_task_assignments,
)
from src.app.modules.tasks.services.task_assignment_service import (
    reserve_task, fetch_task_assignment_by_token, submit_task_assignment
)

from src.app.modules.tasks.services.task_assignment_change_status import (
    accept_task_assignment,
    reject_task_assignment,
    dispute_rejection,
    auditor_won_dispute
)

router = APIRouter(prefix="/task_assignments", tags=["task_assignments"])

@router.get("/users/{user_id}", response_model=List[TaskAssignmentRead])
async def get_task_assignments(session: db_session, user_id: UUID):
    return await fetch_user_task_assignments(session, user_id)

@router.get("/{task_assignment_id}", response_model=TaskAssignmentRead)
async def get_task_assignment(session: db_session, task_assignment_id: UUID):
    return await fetch_task_assignment_by_id(session, task_assignment_id)



@router.post("/reserve", response_model=TaskAssignmentRead, status_code=201)
async def post_reserve_task(session: db_session, user: CurrentUser, task_assignment: TaskAssignmentCreate):
    return await reserve_task(session, task_assignment.task_id, user.user_id)

@router.post("/{token}", response_model=TaskAssignmentRead)
async def post_fetch_task_assignment_by_token(session: db_session, token: str, user: CurrentUser):
    return await fetch_task_assignment_by_token(session, token, user.user_id)

@router.post("/submit/{token}", response_model=TaskAssignmentRead)
async def post_submit_task_assignment(session: db_session, token: str, result_data_json: dict, user: CurrentUser):
    return await submit_task_assignment(session, token, user.user_id, result_data_json)



@router.post("/accept/{assignment_id}", response_model=TaskAssignmentRead)
async def post_accept_task_assignment(session: db_session, assignment_id: UUID):
    return await accept_task_assignment(session, assignment_id)

@router.post("/reject/{assignment_id}", response_model=TaskAssignmentRead)
async def post_reject_task_assignment(session: db_session, assignment_id: UUID):
    return await reject_task_assignment(session, assignment_id)

@router.post("/dispute/{assignment_id}", response_model=TaskAssignmentRead)
async def post_dispute_rejection(session: db_session, assignment_id: UUID):
    return await dispute_rejection(session, assignment_id)

@router.post("/auditor_won_dispute/{assignment_id}", response_model=TaskAssignmentRead)
async def post_auditor_won_dispute(session: db_session, assignment_id: UUID):
    return await auditor_won_dispute(session, assignment_id)




