import uuid
from datetime import datetime
from typing import Any

from sqlmodel import SQLModel
from src.app.modules.tasks.models.Tasks import TaskAnswerType, TaskContentType
from src.app.modules.tasks.models.TaskAssignments import TaskAssignmentStatus


class TaskResourceView(SQLModel):
    id: uuid.UUID
    original_name: str
    url: str


class TaskAssignmentView(SQLModel):
    assignment_id: uuid.UUID
    task_id: uuid.UUID
    status: TaskAssignmentStatus
    expires_at: datetime
    task_content_type: TaskContentType
    task_answer_type: TaskAnswerType
    data_json: dict[str, Any]
    resource_files: list[TaskResourceView]
    result_data_json: dict[str, Any] | None = None


class TaskReserveRequest(SQLModel):
    task_id: uuid.UUID
