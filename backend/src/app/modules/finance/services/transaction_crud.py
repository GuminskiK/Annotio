from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.modules.auth.utils.users_utils import get_user_by_id
from src.app.modules.finance.models.Transaction import Transaction
from sqlmodel import select
from src.app.core.exceptions import TransactionNotFoundException, UserNotFoundException, WalletNotFoundException
from uuid import UUID

async def fetch_transaction_by_id(session: AsyncSession, Transaction_id: UUID, owner_id: UUID):

    user = await get_user_by_id(session, owner_id)

    if not user:
        raise UserNotFoundException()

    if not user.wallet:
        raise WalletNotFoundException()

    result = await session.exec(select(Transaction).where(Transaction.id == Transaction_id, Transaction.wallet_id == user.wallet.user_id))
    transaction = result.one_or_none()

    if not transaction:
        raise TransactionNotFoundException()

    return transaction

async def fetch_transaction_by_id_admin(session: AsyncSession, Transaction_id: UUID):

    result = await session.exec(select(Transaction).where(Transaction.id == Transaction_id))
    transaction = result.one_or_none()

    if not transaction:
        raise TransactionNotFoundException()

    return transaction


async def fetch_user_transactions(session: AsyncSession, owner_id: UUID):

    user = await get_user_by_id(session, owner_id)

    if not user:
        raise UserNotFoundException()

    if not user.wallet:
        raise WalletNotFoundException()

    result = await session.exec(select(Transaction).where(Transaction.wallet_id == user.wallet.user_id))
    return result.all()

async def fetch_all_transactions_admin(session: AsyncSession):

    result = await session.exec(select(Transaction))
    return result.all()


async def fetch_all_user_transactions_admin(session: AsyncSession, user_id: UUID):

    user = await get_user_by_id(session, user_id)

    if not user:
        raise UserNotFoundException()

    if not user.wallet:
        raise WalletNotFoundException()

    result = await session.exec(select(Transaction).where(Transaction.wallet_id == user.wallet.user_id))
    return result.all()
