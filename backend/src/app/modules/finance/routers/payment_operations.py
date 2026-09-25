from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header
from sqlmodel import select

from src.app.deps.dbs import db_session
from src.app.deps.users import AdminUser, CurrentUser
from src.app.modules.finance.models.PaymentOperation import (
    PaymentOperation,
    PaymentOperationComplete,
    PaymentOperationCreate,
    PaymentOperationRead,
)
from src.app.modules.finance.services.payment_operation_service import (
    complete_payment_operation,
    create_payment_operation,
)


router = APIRouter(prefix="/payment-operations", tags=["payment-operations"])


@router.post("", response_model=PaymentOperationRead, status_code=201)
async def post_payment_operation(
    payload: PaymentOperationCreate,
    session: db_session,
    user: CurrentUser,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
):
    return await create_payment_operation(
        session=session,
        user_id=user.user_id,
        operation_type=payload.type.value,
        amount=payload.amount,
        idempotency_key=idempotency_key,
    )


@router.get("/{operation_id}", response_model=PaymentOperationRead)
async def get_payment_operation(
    operation_id: UUID,
    session: db_session,
    user: CurrentUser,
):
    result = await session.exec(
        select(PaymentOperation).where(
            PaymentOperation.id == operation_id,
            PaymentOperation.user_id == user.user_id,
        )
    )
    operation = result.one_or_none()
    if operation is None:
        from src.app.core.exceptions import ResourceNotFoundException
        raise ResourceNotFoundException("Payment operation")
    return operation


@router.post("/{operation_id}/complete", response_model=PaymentOperationRead)
async def complete_payment_operation_for_local_demo(
    operation_id: UUID,
    payload: PaymentOperationComplete,
    session: db_session,
    admin: AdminUser,
):
    """Developer-only completion hook until a real provider webhook exists."""
    return await complete_payment_operation(
        session=session,
        operation_id=operation_id,
        provider_reference=payload.provider_reference,
    )