from decimal import Decimal
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.exceptions import BadRequestException
from src.app.modules.finance.models.Transaction import Transaction, TransactionType
from src.app.core.config import settings
from src.app.modules.finance.utils.finance_utils import _validate_amount, _get_wallet_for_update

async def record_deposit(
    session: AsyncSession,
    user_id: UUID,
    amount: Decimal,
    reference_id: UUID | None = None,
    description: str | None = None,
    commit: bool = True,
) -> Transaction:
    """Credit a wallet after a trusted payment confirmation."""
    amount = _validate_amount(amount)
    wallet = await _get_wallet_for_update(session, user_id)

    if reference_id is not None:
        existing = await session.exec(
            select(Transaction).where(Transaction.reference_id == reference_id)
        )
        previous_transaction = existing.one_or_none()
        if previous_transaction is not None:
            if previous_transaction.wallet_id != wallet.user_id:
                raise BadRequestException("Reference already belongs to another wallet")
            if previous_transaction.amount != amount or previous_transaction.type != TransactionType.DEPOSIT:
                raise BadRequestException("Reference already belongs to another transaction")
            return previous_transaction

    wallet.available_balance += amount

    transaction = Transaction(
        wallet_id=wallet.user_id,
        amount=amount,
        type=TransactionType.DEPOSIT,
        reference_id=reference_id,
        description=description,
    )
    session.add(transaction)
    if commit:
        await session.commit()
        await session.refresh(transaction)
    return transaction

async def record_withdrawal(
    session: AsyncSession,
    user_id: UUID,
    amount: Decimal,
    reference_id: UUID | None = None,
    description: str | None = None,
    commit: bool = True,
) -> Transaction:
    """Debit a wallet after a trusted payment confirmation."""
    amount = _validate_amount(amount)
    wallet = await _get_wallet_for_update(session, user_id)

    if reference_id is not None:
        existing = await session.exec(
            select(Transaction).where(Transaction.reference_id == reference_id)
        )
        previous_transaction = existing.one_or_none()
        if previous_transaction is not None:
            if previous_transaction.wallet_id != wallet.user_id:
                raise BadRequestException("Reference already belongs to another wallet")
            if previous_transaction.amount != amount or previous_transaction.type != TransactionType.WITHDRAWAL:
                raise BadRequestException("Reference already belongs to another transaction")
            return previous_transaction

    if wallet.available_balance < amount:
        raise BadRequestException("Insufficient available balance")

    if amount > Decimal(str(settings.MAX_WITHDRAWAL_AMOUNT_WITHOUT_APPROVAL)):
        # TODO: Implement approval workflow for withdrawals exceeding the limit.
        raise BadRequestException("Withdrawal amount exceeds the maximum allowed without approval")

    wallet.available_balance -= amount

    transaction = Transaction(
        wallet_id=wallet.user_id,
        amount=amount,
        type=TransactionType.WITHDRAWAL,
        reference_id=reference_id,
        description=description,
    )
    session.add(transaction)
    if commit:
        await session.commit()
        await session.refresh(transaction)
    return transaction


async def lock_funds(
    session: AsyncSession,
    user_id: UUID,
    amount: Decimal,
    reference_id: UUID | None = None,
    description: str | None = None,
    commit: bool = True,
) -> Transaction:
    """Move funds from available to locked balance atomically."""
    amount = _validate_amount(amount)
    wallet = await _get_wallet_for_update(session, user_id)
    if wallet.available_balance < amount:
        raise BadRequestException("Insufficient available balance")

    wallet.available_balance -= amount
    wallet.locked_balance += amount
    transaction = Transaction(
        wallet_id=wallet.user_id,
        amount=amount,
        type=TransactionType.LOCK_FUNDS,
        reference_id=reference_id,
        description=description,
    )
    session.add(transaction)
    if commit:
        await session.commit()
        await session.refresh(transaction)
    return transaction


async def release_funds(
    session: AsyncSession,
    user_id: UUID,
    amount: Decimal,
    reference_id: UUID | None = None,
    description: str | None = None,
    commit: bool = True,
) -> Transaction:
    """Return locked funds to the available balance atomically."""
    amount = _validate_amount(amount)
    wallet = await _get_wallet_for_update(session, user_id)
    if wallet.locked_balance < amount:
        raise BadRequestException("Insufficient locked balance")

    wallet.locked_balance -= amount
    wallet.available_balance += amount
    transaction = Transaction(
        wallet_id=wallet.user_id,
        amount=amount,
        type=TransactionType.RELEASE_FUNDS,
        reference_id=reference_id,
        description=description,
    )
    session.add(transaction)
    if commit:
        await session.commit()
        await session.refresh(transaction)
    return transaction