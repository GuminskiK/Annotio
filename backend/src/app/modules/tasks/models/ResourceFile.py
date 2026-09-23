import uuid
from typing import TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .Task import Task

class ResourceFileBase(SQLModel):
    task_id: uuid.UUID = Field(foreign_key="task.id", index=True)
    storage_path: str
    original_name: str
    retention_period: datetime | None = None


class ResourceFile(ResourceFileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task: "Task" = Relationship(back_populates="resource_files")

class ResourceFileCreate(ResourceFileBase):
    pass


class ResourceFileRead(ResourceFileBase):
    id: uuid.UUID
