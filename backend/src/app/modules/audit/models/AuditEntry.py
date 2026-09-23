import uuid
from enum import Enum
from sqlmodel import SQLModel, Field


class DecisionType(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class AuditEntryBase(SQLModel):
    assignment_id: uuid.UUID = Field(foreign_key="taskassignment.id", index=True)
    auditor_id: uuid.UUID = Field(index=True)
    decision: DecisionType
    reason: str | None = None


class AuditEntry(AuditEntryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class AuditEntryCreate(AuditEntryBase):
    pass


class AuditEntryRead(AuditEntryBase):
    id: uuid.UUID

