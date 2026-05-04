import uuid
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .Users import User

class ConsentType(Enum):
    MARKETING = "marketing"
    LEGAL = "legal"

class UserConsentBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    consent: ConsentType
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserConsent(UserConsentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user: "User" = Relationship(back_populates="consents")

class UserConsentCreate(UserConsentBase):
    pass

class UserConsentRead(UserConsentBase):
    id: uuid.UUID