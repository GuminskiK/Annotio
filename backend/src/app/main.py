from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.app.core.config import settings
from src.app.core.health import check_db, check_disk, check_redis
from src.app.core.logger import setup_logging
from src.app.core.logging_middleware import StructlogMiddleware
from src.app.core.rate_limiting import custom_rate_limit_handler, limiter
from src.app.deps.dbs import db_deps, db_session, redis_client
from src.app.modules.auth.routers import apikeys, auth, sessions, two_fa, users
from src.app.modules.finance.routers import payment_operations, transactions, wallet

setup_logging(json_logs=False, log_level="INFO")  # SET json_logs=True for Sentry/Loki!

@asynccontextmanager
async def lifespan(app: FastAPI):
    import json

    from sqlalchemy.orm import selectinload
    from sqlmodel import SQLModel, select
    from src.app.modules.auth.models.BackupCodes import BackupCode
    from src.app.modules.auth.models.Users import Role, User
    from src.app.modules.auth.utils.auth_utils import get_password_hash
    from src.app.modules.auth.utils.users_utils import get_blind_index

    async with db_deps.engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    async with db_deps.AsyncSessionLocal() as session:
        query = select(User).options(selectinload(User.api_keys)) # type: ignore[arg-type]
        result = await session.exec(query)
        users_with_keys = result.all()

        for user in users_with_keys:
            for api_key in user.api_keys or []:
                await db_deps.get_redis().set(
                    f"apikey:{api_key.hashed_key}",
                    json.dumps({
                        "id": str(api_key.user_id),
                        "username": user.username,
                        "role": str(user.role),
                    }),
                )

        query_users = select(User)
        result_users = await session.exec(query_users)

        if not result_users.first():
            admin_email = f"{settings.ADMIN_USERNAME}@example.com"

            admin_user = User(
                username=settings.ADMIN_USERNAME,
                email=admin_email,

                role=Role.ADMIN,
                is_activated=True,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                email_blind_index=get_blind_index(admin_email),
                is_totp_enabled=False,
            )

            session.add(admin_user)
            await session.commit()

    yield

app = FastAPI(
    lifespan=lifespan,     
    title=settings.APP_NAME,
    root_path="/api")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(StructlogMiddleware)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(apikeys.router)
app.include_router(two_fa.router)
app.include_router(sessions.router)
app.include_router(payment_operations.router)
app.include_router(transactions.router)
app.include_router(wallet.router)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
async def health(redis: redis_client, db: db_session):
    result = {"status": "ok", "checks": {}}

    # Disk usage
    disk_ok, disk_info = check_disk()
    result["checks"]["disk"] = disk_info
    if not disk_ok:
        result["status"] = "degraded"

    # DB Check
    db_ok, db_info = await check_db(db)
    result["checks"]["db"] = {"ok": db_ok, "info": db_info}
    if not db_ok:
        result["status"] = "down"

    # Redis Check
    redis_ok, redis_info = await check_redis(redis)
    result["checks"]["redis"] = {"ok": redis_ok, "info": redis_info}
    if not redis_ok:
        result["status"] = "down"

    return result
