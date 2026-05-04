import uuid
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .Users import User

class UserProfileBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True, unique=True)
    personal_data: str | None = Field(
        default=None, 
        description="Encrypted String (Imię, nazwisko, adres – szyfrowane zgodnie z RODO)"
    )

class UserProfile(UserProfileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    anonymized_at: datetime | None = Field(
        default=None, 
        description="Timestamp (Data anonimizacji po usunięciu konta)"
    )
    user: Optional["User"] = Relationship(back_populates="profile")

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileRead(UserProfileBase):
    id: uuid.UUID
    anonymized_at: datetime | None

class UserProfileUpdate(SQLModel):
    personal_data: str | None = None
