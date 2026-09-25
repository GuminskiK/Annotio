import uuid
from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .Wallet import Wallet

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    PAYOUT = "PAYOUT"
    LOCK_FUNDS = "LOCK_FUNDS"
    RELEASE_FUNDS = "RELEASE_FUNDS"


class TransactionStatus(str, Enum):
    COMPLETED = "COMPLETED"


class TransactionBase(SQLModel):
    wallet_id: uuid.UUID = Field(foreign_key="wallet.user_id", index=True)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    type: TransactionType
    status: TransactionStatus = Field(default=TransactionStatus.COMPLETED)
    reference_id: uuid.UUID | None = Field(default=None, index=True, unique=True)
    description: str | None = Field(default=None, max_length=255)


class Transaction(TransactionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    wallet: "Wallet" = Relationship(back_populates="transactions")


class TransactionRead(TransactionBase):
    id: uuid.UUID
    created_at: datetime
