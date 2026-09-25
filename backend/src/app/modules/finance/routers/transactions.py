from typing import List
from uuid import UUID

from fastapi import APIRouter
from src.app.modules.auth.models.Users import Role
from src.app.deps.dbs import db_session
from src.app.deps.users import CurrentUser, AdminUser
from src.app.modules.finance.models.Transaction import TransactionRead
from src.app.modules.finance.services.transaction_crud import (
    fetch_all_transactions_admin,
    fetch_transaction_by_id_admin,
    fetch_transaction_by_id,
    fetch_user_transactions

)

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("", response_model=List[TransactionRead])
async def get_transactions(session: db_session, user: CurrentUser, admin: AdminUser):

    return await fetch_all_transactions_admin(session)


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(session: db_session, user: CurrentUser, transaction_id: UUID):

    if user.role == Role.ADMIN:
        return await fetch_transaction_by_id_admin(session, transaction_id)

    return await fetch_transaction_by_id(session, transaction_id, user.user_id)

@router.get("/user/{user_id}", response_model=List[TransactionRead])
async def get_transaction_user_transactions(session: db_session, user: CurrentUser, user_id: UUID):

    if user.role != Role.ADMIN:
        user_id = user.user_id

    return await fetch_user_transactions(session, user_id)
