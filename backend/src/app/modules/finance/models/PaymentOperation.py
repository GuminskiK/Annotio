import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, SQLModel


class PaymentOperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


class PaymentOperationStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PaymentOperation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    type: PaymentOperationType
    status: PaymentOperationStatus = Field(default=PaymentOperationStatus.PENDING)
    provider: str = Field(default="manual", max_length=50)
    provider_reference: str | None = Field(default=None, unique=True, index=True)
    idempotency_key: str | None = Field(default=None, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)


class PaymentOperationCreate(SQLModel):
    type: PaymentOperationType
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class PaymentOperationRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    type: PaymentOperationType
    status: PaymentOperationStatus
    provider: str
    provider_reference: str | None
    created_at: datetime
    completed_at: datetime | None


class PaymentOperationComplete(SQLModel):
    provider_reference: str | None = None