from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from decimal import Decimal

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ADMIN_USERNAME: str = "admin123"
    ADMIN_PASSWORD: str = "changeme"

    # Session settings
    SESSION_SECRET_KEY: str = "your-super-strategic-secret-key-change-this"
    SESSION_TTL: int = 48 * 3600
    SESSION_COOKIE_NAME: str = "homeos_session"
    SESSION_SAME_SITE: Literal['lax', 'strict', 'none'] = "lax"
    SESSION_HTTP_ONLY: bool = True
    SESSION_SECURE: bool = False

    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str = "noreply@localhost.com"
    MAIL_PORT: int = 1025
    MAIL_SERVER: str = "localhost"
    FRONTEND_URL: str = "http://localhost:3000"

    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    APP_NAME: str = "Annotio"

    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_TTL: int = 3600  # seconds

    DUMMY_HASH: str = "$argon2id$v=19$m=65536,t=2,p=2$Wm9uZQ$Wm9uZQ"
    ACTIVATE_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60

    MAX_WITHDRAWAL_AMOUNT_WITHOUT_APPROVAL: Decimal = Decimal("200.00")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()
