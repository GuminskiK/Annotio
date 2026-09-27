import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ...auth.models.Users import User
    from .Tasks import Task

class TaskAssignmentStatus(str, Enum):
    RESERVED = "RESERVED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TaskAssignmentBase(SQLModel):
    task_id: uuid.UUID = Field(foreign_key="task.id", index=True)
    worker_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    status: TaskAssignmentStatus = Field(default=TaskAssignmentStatus.RESERVED)
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=30))
    result_data_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

class TaskAssignment(TaskAssignmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reserved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    token: str = Field(default_factory=lambda: hashlib.sha256(secrets.token_urlsafe(32).encode()).hexdigest())
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
    result_data_json: dict[str, Any] | None = None
    submitted_at: datetime | None = None
