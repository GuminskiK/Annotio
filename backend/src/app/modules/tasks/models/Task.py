import uuid
from typing import TYPE_CHECKING, Any, Dict, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from ...campaigns.models.Campaign import Campaign
    from .ResourceFile import ResourceFile
    from .TaskAssignment import TaskAssignment

class TaskBase(SQLModel):
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id", index=True)
    data_json: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    reward: Decimal = Field(default=0, max_digits=10, decimal_places=2)


class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign: "Campaign" = Relationship(back_populates="tasks")
    resource_files: List["ResourceFile"] = Relationship(back_populates="task")
    assignments: List["TaskAssignment"] = Relationship(back_populates="task")

class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: uuid.UUID


class TaskUpdate(SQLModel):
    data_json: Dict[str, Any] | None = None
    reward: Decimal | None = None
