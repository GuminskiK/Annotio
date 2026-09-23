from sqlmodel import Field, SQLModel
from uuid import uuid4, UUID

class BackupCode(SQLModel):
    id: UUID = Field(default_factory=uuid4, index=True, primary_key=True, nullable=False)
    user_id: UUID = Field(foreign_key="user.id")
    code_hash: str = Field(max_length=256)