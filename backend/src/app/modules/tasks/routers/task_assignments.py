from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from src.app.deps.dbs import db_session
from src.app.deps.users import CurrentUser
from src.app.modules.tasks.models.TaskAssignments import (
    TaskAssignmentCreate,
    TaskAssignmentRead,
)
from src.app.modules.tasks.models.TaskViews import TaskAssignmentView, TaskReserveRequest
from src.app.modules.tasks.services.task_assignment_change_status import (
    accept_task_assignment,
    auditor_won_dispute,
    dispute_rejection,
    reject_task_assignment,
)
from src.app.modules.tasks.services.task_assignment_crud import (
    fetch_task_assignment_by_id,
    fetch_user_task_assignments,
)
from src.app.modules.tasks.services.task_assignment_service import (
    fetch_task_assignment_view,
    fetch_task_assignment_by_token,
    reserve_task,
    submit_task_assignment,
)
from src.app.core.storage import object_storage

router = APIRouter(prefix="/task_assignments", tags=["task_assignments"])

@router.get("/users/{user_id}", response_model=list[TaskAssignmentRead])
async def get_task_assignments(session: db_session, user_id: UUID):
    return await fetch_user_task_assignments(session, user_id)

@router.get("/{task_assignment_id}", response_model=TaskAssignmentRead)
async def get_task_assignment(session: db_session, task_assignment_id: UUID):
    return await fetch_task_assignment_by_id(session, task_assignment_id)



@router.post("/reserve", response_model=TaskAssignmentRead, status_code=201)
async def post_reserve_task(session: db_session, user: CurrentUser, request: TaskReserveRequest):
    return await reserve_task(session, request.task_id, user.user_id)


@router.get("/{assignment_id}/view", response_model=TaskAssignmentView)
async def get_assignment_view(session: db_session, user: CurrentUser, assignment_id: UUID):
    role = getattr(user.role, "value", str(user.role)).lower()
    access_user_id = None if role in {"admin", "auditor"} else user.user_id
    return await fetch_task_assignment_view(session, assignment_id, access_user_id)


@router.get("/{assignment_id}/files/{resource_id}")
async def get_assignment_file(session: db_session, user: CurrentUser, assignment_id: UUID, resource_id: UUID):
    role = getattr(user.role, "value", str(user.role)).lower()
    access_user_id = None if role in {"admin", "auditor"} else user.user_id
    resource = await fetch_task_assignment_view(session, assignment_id, access_user_id, resource_id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    data, content_type = await object_storage.download(resource)
    return Response(content=data, media_type=content_type)

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




