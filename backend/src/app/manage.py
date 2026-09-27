import argparse
import asyncio

from src.app.core.exceptions import UserNotFoundException
from src.app.deps.dbs import db_deps, redis_pure
from src.app.modules.auth.models.CurrentUserContext import CurrentUserContext
from src.app.modules.auth.models.Users import UserUpdate
from src.app.modules.auth.services.users_service import update_user
from src.app.modules.auth.utils.users_utils import get_user_by_username


async def reset_password(args):

    if args.command == "reset-password":
        userUpdate = UserUpdate(
            username = args.username,
            plain_password= args.new_password,
            is_blocked = False,
            email = args.email
        )

        AsyncSessionLocal = db_deps.AsyncSessionLocal()

        async with AsyncSessionLocal as session:
            user = await get_user_by_username(session, args.username)

            if not user:
                raise UserNotFoundException()
            
            # context = CurrentUserContext(
            #     session_id="reset-password-session",
            #     user_id=user.id,
            #     username=args.username,
            #     role=user.role,
            #     is_totp_enabled=False
            # )

            await update_user(
                redis_pure,
                session,
                userUpdate,
                user.id
            )

            user.is_totp_enabled = False
            session.add(user)
            await session.commit()

        print(f"Password for user '{args.username}' has been reset successfully.")

        if hasattr(redis_pure, "aclose"):
            await redis_pure.aclose()
        else:
            await redis_pure.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Zarządzanie aplikacją HomeOS")
    subparsers = parser.add_subparsers(dest="command")

    # Rejestracja podkomendy reset-password
    reset_parser = subparsers.add_parser("reset-password")
    reset_parser.add_argument("--username", required=True, help="Nazwa użytkownika")
    reset_parser.add_argument("--email", required=True, help="Email użytkownika")
    reset_parser.add_argument("--new-password", required=True, help="Nowe hasło")

    args = parser.parse_args()
    asyncio.run(reset_password(args))