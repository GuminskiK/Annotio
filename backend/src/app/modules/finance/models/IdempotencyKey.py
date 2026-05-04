from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional

class IdempotencyKey(SQLModel, table=True):
    id: str = Field(primary_key=True) 
    user_id: UUID = Field(index=True)
    
    response_code: int
    response_body: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=24)
    )