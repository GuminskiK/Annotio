from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.exceptions import BadRequestException

from src.app.modules.finance.utils.finance_utils import _validate_amount
from src.app.modules.finance.services.transaction_service import (
    record_deposit,
    record_withdrawal,
)
from src.app.modules.finance.models.PaymentOperation import (
    PaymentOperation,
    PaymentOperationStatus,
)

async def create_payment_operation(
    session: AsyncSession,
    user_id: UUID,
    operation_type: str,
    amount: Decimal,
    idempotency_key: str,
    provider: str = "manual",
) -> PaymentOperation:
    """Create a pending operation requested by the frontend."""
    amount = _validate_amount(amount)
    if not idempotency_key.strip():
        raise BadRequestException("Idempotency key is required")

    existing = await session.exec(
        select(PaymentOperation).where(
            PaymentOperation.idempotency_key == idempotency_key,
            PaymentOperation.user_id == user_id,
        )
    )
    previous_operation = existing.one_or_none()
    if previous_operation is not None:
        if previous_operation.amount != amount or previous_operation.type.value != operation_type:
            raise BadRequestException("Idempotency key belongs to another operation")
        return previous_operation

    try:
        from src.app.modules.finance.models.PaymentOperation import PaymentOperationType
        parsed_type = PaymentOperationType(operation_type)
    except ValueError as error:
        raise BadRequestException("Unsupported payment operation type") from error

    operation = PaymentOperation(
        user_id=user_id,
        amount=amount,
        type=parsed_type,
        provider=provider,
        idempotency_key=idempotency_key,
    )
    session.add(operation)
    await session.commit()
    await session.refresh(operation)
    return operation


async def complete_payment_operation(
    session: AsyncSession,
    operation_id: UUID,
    provider_reference: str | None = None,
) -> PaymentOperation:
    """Complete a trusted operation and create its immutable ledger entry."""
    result = await session.exec(
        select(PaymentOperation)
        .where(PaymentOperation.id == operation_id)
        .with_for_update()
    )
    operation = result.one_or_none()
    if operation is None:
        raise BadRequestException("Payment operation not found")
    if operation.status == PaymentOperationStatus.COMPLETED:
        return operation
    if operation.status == PaymentOperationStatus.FAILED:
        raise BadRequestException("Payment operation has already failed")

    if operation.type.value == "DEPOSIT":
        await record_deposit(
            session,
            operation.user_id,
            operation.amount,
            reference_id=operation.id,
            description=f"Payment operation {operation.id}",
            commit=False,
        )
    else:
        await record_withdrawal(
            session,
            operation.user_id,
            operation.amount,
            reference_id=operation.id,
            description=f"Payment operation {operation.id}",
            commit=False,
        )

    operation.status = PaymentOperationStatus.COMPLETED
    operation.provider_reference = provider_reference
    operation.completed_at = datetime.utcnow()
    session.add(operation)
    await session.commit()
    await session.refresh(operation)
    return operation