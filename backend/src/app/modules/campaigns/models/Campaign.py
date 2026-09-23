from typing import TYPE_CHECKING, List, Optional
from sqlmodel import JSON, Column, Field, Relationship, SQLModel
from decimal import Decimal
from enum import Enum
import uuid

if TYPE_CHECKING:
    from ...auth.models.Users import User
    from ...tasks.models.Task import Task

class AcceptanceStrategy(Enum):
    AUTO_48H = "auto_48h"
    AUDITOR_REQUIRED = "auditor_required"

class CampaignStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"

class CampaignBase(SQLModel):
    client_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    title: str
    description: str
    total_budget: Decimal
    acceptance_strategy: AcceptanceStrategy
    status: CampaignStatus

class Campaign(CampaignBase, table = True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client: "User" = Relationship(back_populates="campaigns")
    tasks: List["Task"] = Relationship(back_populates="campaign")

class CampaignCreate(CampaignBase):
    pass

class CampaignRead(CampaignBase):
    id: uuid.UUID

class CampaignUpdate(SQLModel):
    title: str | None = None
    decription: str | None = None
    total_budget: Decimal | None = None
    acceptance_strategy: AcceptanceStrategy | None = None
    status: CampaignStatus | None = None
