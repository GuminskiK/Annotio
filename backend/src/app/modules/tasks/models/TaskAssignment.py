import uuid
from typing import TYPE_CHECKING, Any, Dict
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from ...auth.models.Users import User
    from .Task import Task

class TaskAssignmentStatus(str, Enum):
    RESERVED = "RESERVED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class TaskAssignmentBase(SQLModel):
    task_id: uuid.UUID = Field(foreign_key="task.id", index=True)
    worker_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    status: TaskAssignmentStatus = Field(default=TaskAssignmentStatus.RESERVED)
    expires_at: datetime | None = None
    result_data_json: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

class TaskAssignment(TaskAssignmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reserved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: datetime | None = None
    task: "Task" = Relationship(back_populates="assignments")
    worker: "User" = Relationship(back_populates="task_assignments")

class TaskAssignmentCreate(TaskAssignmentBase):
    pass


class TaskAssignmentRead(TaskAssignmentBase):
    id: uuid.UUID
    reserved_at: datetime
    submitted_at: datetime | None


class TaskAssignmentUpdate(SQLModel):
    status: TaskAssignmentStatus | None = None
    result_data_json: Dict[str, Any] | None = None
    submitted_at: datetime | None = None
