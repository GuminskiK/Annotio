from datetime import datetime, timedelta
from uuid import UUID

from sqlmodel import Field, SQLModel


class IdempotencyKey(SQLModel, table=True):
    id: str = Field(primary_key=True) 
    user_id: UUID = Field(index=True)
    
    response_code: int
    response_body: str
    
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(hours=24)
    )