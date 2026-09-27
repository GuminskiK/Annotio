import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.finance.models.Wallet import Wallet

    from .APIKeys import APIKey
    from .BackupCodes import BackupCode

USERNAME_PATTERN = r"^[a-zA-Z0-9_\-]+$"

def validate_password_strength(v: str) -> str:
    if not v:
        return v
    if len(v) < 8:
        raise ValueError("Hasło musi mieć co najmniej 8 znaków")
    if not any(c.isupper() for c in v):
        raise ValueError("Hasło musi posiadać przynajmniej jedną dużą literę")
    if not any(c.islower() for c in v):
        raise ValueError("Hasło musi posiadać przynajmniej jedną małą literę")
    if not any(c.isdigit() for c in v):
        raise ValueError("Hasło musi posiadać przynajmniej jedną cyfrę")
    if not any(not c.isalnum() for c in v):
        raise ValueError("Hasło musi posiadać przynajmniej jeden znak specjalny")
    return v

class Role (Enum):
    ADMIN = "admin"
    CLIENT = "client"
    WORKER = "worker"
    AUDITOR = "auditor"

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, min_length=3, max_length=40, regex=USERNAME_PATTERN)
    email: EmailStr = Field(unique=True)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory= uuid.uuid4, primary_key=True)
    role: Role = Field(default = Role.WORKER)
    is_activated: bool = Field(default = False)
    is_blocked: bool = Field(default=False)

    hashed_password: str = Field()
    email_blind_index: str

    totp_secret: str | None = Field(default=None)
    is_totp_enabled: bool = Field(default=False)

    avatar_url: str | None = Field(default=None)

    backup_codes: list["BackupCode"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    api_keys: list["APIKey"] = Relationship(back_populates="owner")
    # profile: Optional["UserProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    # consents: List["UserConsent"] = Relationship(back_populates="user")
    wallet: Optional["Wallet"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    # campaigns: List["Campaign"] = Relationship(back_populates="client")
    # task_assignments: List["TaskAssignment"] = Relationship(back_populates="worker")

class UserCreate(UserBase):
    plain_password: str

    @field_validator("plain_password")
    @classmethod
    def check_password(cls, v):
        return validate_password_strength(v)

class UserRead(UserBase):
    id: uuid.UUID
    role: Role
    is_activated: bool
    is_totp_enabled: bool

class UserUpdate(SQLModel):
    username: str | None = Field(default=None, min_length=3, max_length=40, regex=USERNAME_PATTERN)
    plain_password: str | None = None
    is_blocked: bool | None = None
    email: EmailStr | None = Field(unique=True)

    @field_validator("plain_password")
    @classmethod
    def check_password(cls, v):
        if v is not None:
            return validate_password_strength(v)
        return v

class NewPasswordModel(SQLModel):
    plain_password: str

    @field_validator("plain_password")
    @classmethod
    def check_password(cls, v):
        return validate_password_strength(v)
