from decimal import Decimal
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.exceptions import BadRequestException, WalletNotFoundException
from src.app.modules.finance.models.Wallet import Wallet

def _validate_amount(amount: Decimal) -> Decimal:
    amount = Decimal(amount)
    if amount <= 0:
        raise BadRequestException("Amount must be greater than zero")
    return amount


async def _get_wallet_for_update(session: AsyncSession, user_id: UUID) -> Wallet:
    result = await session.exec(
        select(Wallet).where(Wallet.user_id == user_id).with_for_update()
    )
    wallet = result.one_or_none()
    if wallet is None:
        raise WalletNotFoundException()
    return wallet