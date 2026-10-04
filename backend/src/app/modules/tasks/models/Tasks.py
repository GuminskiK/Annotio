import uuid
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ...campaigns.models.Campaigns import Campaign
    from .ResourceFile import ResourceFile
    from .TaskAssignments import TaskAssignment

class TaskContentType (Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"

class TaskAnswerType (Enum):
    TEXT = "text"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"

class TaskBase(SQLModel):
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id", index=True)
    data_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    reward: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    required_assignments: int = Field(default=1)
    time_limit_minutes: int = Field(default=30)

    task_content_type: TaskContentType = Field(default=TaskContentType.TEXT)
    task_answer_type: TaskAnswerType = Field(default=TaskAnswerType.TEXT)

    owner_id: uuid.UUID = Field(foreign_key="user.id", index=True)


class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign: "Campaign" = Relationship(back_populates="tasks")
    resource_files: list["ResourceFile"] = Relationship(back_populates="task")
    assignments: list["TaskAssignment"] = Relationship(back_populates="task")

class TaskCreate(TaskBase):
    owner_id: uuid.UUID | None = None


class TaskRead(TaskBase):
    id: uuid.UUID


class TaskPage(SQLModel):
    items: list[TaskRead]
    total: int
    page: int
    page_size: int
    pages: int


class TaskUpdate(SQLModel):
    data_json: dict[str, Any] | None = None
    reward: Decimal | None = None
    required_assignments: int | None = None
