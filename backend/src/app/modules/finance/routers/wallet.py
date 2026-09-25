from fastapi import APIRouter
from sqlmodel import select

from src.app.core.exceptions import WalletNotFoundException
from src.app.deps.dbs import db_session
from src.app.deps.users import CurrentUser
from src.app.modules.finance.models.Wallet import Wallet, WalletRead


router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletRead)
async def get_wallet(session: db_session, user: CurrentUser):
    result = await session.exec(select(Wallet).where(Wallet.user_id == user.user_id))
    wallet = result.one_or_none()
    if wallet is None:
        raise WalletNotFoundException()
    return wallet