import uuid
from typing import TYPE_CHECKING
from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .Wallet import Wallet

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    PAYOUT = "PAYOUT"
    LOCK_FUNDS = "LOCK_FUNDS"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TransactionBase(SQLModel):
    wallet_id: uuid.UUID = Field(foreign_key="wallet.user_id", index=True)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    type: TransactionType
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)


class Transaction(TransactionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    wallet: "Wallet" = Relationship(back_populates="transactions")

class TransactionCreate(TransactionBase):
    pass


class TransactionRead(TransactionBase):
    id: uuid.UUID


class TransactionUpdate(SQLModel):
    status: TransactionStatus | None = None
