import uuid
from typing import TYPE_CHECKING, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from ...auth.models.Users import User
    from .Transaction import Transaction

class WalletBase(SQLModel):
    available_balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    locked_balance: Decimal = Field(default=0, max_digits=12, decimal_places=2)

class Wallet(WalletBase, table=True):
    user_id: uuid.UUID = Field(primary_key=True, foreign_key="user.id")
    user: "User" = Relationship(back_populates="wallet")
    transactions: List["Transaction"] = Relationship(back_populates="wallet")


class WalletCreate(WalletBase):
    user_id: uuid.UUID


class WalletRead(WalletBase):
    user_id: uuid.UUID


class WalletUpdate(SQLModel):
    available_balance: Decimal | None = None
    locked_balance: Decimal | None = None
