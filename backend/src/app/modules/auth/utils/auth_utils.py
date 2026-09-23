from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
)


def get_password_hash(plain: str) -> str:
    """Generuje hash z podanego hasła."""
    return ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Weryfikuje, czy podane hasło odpowiada hashowi."""
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        return False