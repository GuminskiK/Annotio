from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import uuid4, UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Users import User

class APIKey(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, index=True, primary_key=True, nullable=False)

    name: str = Field(nullable=False)

    hashed_key: str = Field(unique=True, index=True, nullable=False)
    key_hint: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_used_at: Optional[datetime] = Field(default=None)

    user_id: UUID = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="api_keys")