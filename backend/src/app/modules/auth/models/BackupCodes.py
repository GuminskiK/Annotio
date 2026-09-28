from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Users import User


class BackupCode(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, index=True, primary_key=True, nullable=False)
    user_id: UUID = Field(foreign_key="user.id")
    code_hash: str = Field(max_length=256)
    user: "User" = Relationship(back_populates="backup_codes")