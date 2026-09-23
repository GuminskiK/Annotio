from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid

if TYPE_CHECKING:
    from ...auth.models.Users import User

class Action(Enum):
    OPEN_FILE = "open_file"

class AccessLogBase(SQLModel):
    file_id: uuid.UUID = Field(index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    action: Action

class AccessLog(AccessLogBase, table = True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Optional["User"] = Relationship()

class AccessLogCreate(AccessLogBase):
    pass

class AccessLogRead(AccessLogBase):
    id: int
    timestamp: datetime
