import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from ...campaigns.models.Campaigns import Campaign
    from .ResourceFile import ResourceFile
    from .TaskAssignments import TaskAssignment

class TaskBase(SQLModel):
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id", index=True)
    data_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    reward: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    required_assignments: int = Field(default=1)
    time_limit_minutes: int = Field(default=30)

    owner_id: uuid.UUID = Field(foreign_key="user.id", index=True)


class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign: "Campaign" = Relationship(back_populates="tasks")
    resource_files: list["ResourceFile"] = Relationship(back_populates="task")
    assignments: list["TaskAssignment"] = Relationship(back_populates="task")

class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: uuid.UUID


class TaskUpdate(SQLModel):
    data_json: dict[str, Any] | None = None
    reward: Decimal | None = None
    required_assignments: int | None = None
