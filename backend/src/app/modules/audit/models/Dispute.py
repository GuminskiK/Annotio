import uuid
from enum import Enum
from sqlmodel import SQLModel, Field


class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED_ACCEPTED = "RESOLVED_ACCEPTED"
    RESOLVED_REJECTED = "RESOLVED_REJECTED"


class DisputeBase(SQLModel):
    assignment_id: uuid.UUID = Field(foreign_key="taskassignment.id", unique=True)
    worker_reason: str
    status: DisputeStatus = Field(default=DisputeStatus.OPEN)


class Dispute(DisputeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class DisputeCreate(DisputeBase):
    pass


class DisputeRead(DisputeBase):
    id: uuid.UUID


class DisputeUpdate(SQLModel):
    status: DisputeStatus | None = None
