import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext
from uuid import UUID
from src.app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=65536,
    argon2__parallelism=2,
)


ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
APP_NAME = settings.APP_NAME

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(plain: str) -> str:
    return pwd_context.hash(plain)


def create_token(
    user_id: UUID, 
    username: str,
    token_type: str, 
    expires_delta: timedelta
) -> str:
    expire = _now() + expires_delta
    jti = str(uuid.uuid4())
    
    to_encode = {
        "id": user_id,
        "iat": int(_now().timestamp()),
        "exp": int(expire.timestamp()),
        "iss": APP_NAME,
        "aud": APP_NAME + "-api",
        "jti": jti,
        "typ": token_type,
        "sub": username
    }
        
    return encode_token(to_encode)


def encode_token(to_encode: dict) -> str:
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=APP_NAME + "-api", issuer=APP_NAME)