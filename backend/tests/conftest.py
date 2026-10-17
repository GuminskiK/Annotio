import os
from collections.abc import AsyncGenerator
from decimal import Decimal
from typing import Any, get_args
from uuid import UUID, uuid4

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.rate_limiting import limiter
from src.app.deps.dbs import db_deps
from src.app.deps.users import AdminUser, CurrentUser, auth_dependency
from src.app.main import app
from src.app.modules.auth.models.CurrentUserContext import CurrentUserContext
from src.app.modules.auth.models.Users import Role, User
from src.app.modules.auth.services.email_service import fm
from src.app.modules.finance.models.PaymentOperation import (
    PaymentOperation,
    PaymentOperationType,
)
from src.app.modules.finance.models.Transaction import Transaction, TransactionType
from src.app.modules.finance.models.Wallet import Wallet
from src.app.core.storage import object_storage
from src.app.modules.auth.utils.auth_utils import get_password_hash
from src.app.modules.auth.utils.users_utils import get_blind_index

limiter.enabled = False

TEST_USER_USERNAME = "TestUser"
TEST_USER_EMAIL = "TestUser@example.com"
TEST_USER_PASSWORD = "TestPassword123!"


class FakeAsyncRedis:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}
        self.expires: dict[str, int] = {}

    async def set(self, name: str, value: Any, ex: int | None = None, **_: Any) -> bool:
        self.data[name] = value
        if ex is not None:
            self.expires[name] = ex
        return True

    async def setex(self, name: str, time: int, value: Any) -> bool:
        return await self.set(name, value, ex=time)

    async def get(self, name: str) -> Any:
        return self.data.get(name)

    async def delete(self, *names: str) -> int:
        deleted = 0
        for name in names:
            if name in self.data:
                deleted += 1
            self.data.pop(name, None)
            self.expires.pop(name, None)
        return deleted

    async def exists(self, name: str) -> int:
        return int(name in self.data)

    async def expire(self, name: str, time: int) -> bool:
        if name not in self.data:
            return False
        self.expires[name] = time
        return True

    async def ttl(self, name: str) -> int:
        return self.expires.get(name, -1)

    async def sadd(self, name: str, *values: str) -> int:
        current = self.data.setdefault(name, set())
        before = len(current)
        current.update(values)
        return len(current) - before

    async def smembers(self, name: str) -> set[str]:
        return self.data.get(name, set())

    async def srem(self, name: str, *values: str) -> int:
        current = self.data.get(name, set())
        removed = 0
        for value in values:
            if value in current:
                current.remove(value)
                removed += 1
        return removed

    async def hset(self, name: str, mapping: dict[str, Any]) -> int:
        current = self.data.setdefault(name, {})
        current.update(mapping)
        return len(mapping)

    async def hget(self, name: str, key: str) -> Any:
        return self.data.get(name, {}).get(key)

    async def hgetall(self, name: str) -> dict[str, Any]:
        return self.data.get(name, {})

    async def sismember(self, name: str, value: str) -> bool:
        return value in self.data.get(name, set())

    async def aclose(self) -> None:
        return None


class FakeMailpit:
    def __init__(self) -> None:
        self.messages: list[Any] = []

    async def send_message(self, message: Any, *args: Any, **kwargs: Any) -> None:
        self.messages.append(message)


class FakeObjectStorage:
    def __init__(self) -> None:
        self.objects: dict[str, tuple[bytes, str]] = {}

    async def ensure_bucket(self) -> None:
        return None

    async def upload(self, data: bytes, filename: str, content_type: str, prefix: str = "tasks") -> str:
        object_name = f"{prefix}/{uuid4()}/{filename}"
        self.objects[object_name] = (data, content_type)
        return object_name

    async def download(self, object_name: str) -> tuple[bytes, str]:
        return self.objects[object_name]


engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _make_metadata_sqlite_compatible() -> None:
    for table in SQLModel.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, JSONB):
                column.type = JSON()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    _make_metadata_sqlite_compatible()
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def fake_redis() -> FakeAsyncRedis:
    return FakeAsyncRedis()


@pytest.fixture
def mailpit(monkeypatch: pytest.MonkeyPatch) -> FakeMailpit:
    fake = FakeMailpit()
    monkeypatch.setattr(fm, "send_message", fake.send_message)
    return fake


@pytest.fixture
def localstack(monkeypatch: pytest.MonkeyPatch) -> FakeObjectStorage:
    fake = FakeObjectStorage()
    monkeypatch.setattr(object_storage, "ensure_bucket", fake.ensure_bucket)
    monkeypatch.setattr(object_storage, "upload", fake.upload)
    monkeypatch.setattr(object_storage, "download", fake.download)
    return fake


@pytest.fixture
def s3_storage(localstack: FakeObjectStorage) -> FakeObjectStorage:
    return localstack


@pytest.fixture
def client(db_session: AsyncSession, fake_redis: FakeAsyncRedis, mailpit: FakeMailpit, localstack: FakeObjectStorage):
    async def override_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    def override_redis() -> FakeAsyncRedis:
        return fake_redis

    app.dependency_overrides[db_deps.get_session] = override_session
    app.dependency_overrides[db_deps.get_redis] = override_redis
    original_auth_redis = auth_dependency.redis
    original_engine = db_deps.engine
    original_session_factory = db_deps.AsyncSessionLocal
    original_redis = db_deps.redis_url
    setattr(auth_dependency, "redis", fake_redis)
    db_deps.engine = engine
    db_deps.AsyncSessionLocal = TestingSessionLocal
    setattr(db_deps, "redis_url", fake_redis)
    with TestClient(app) as test_client:
        yield test_client
    db_deps.engine = original_engine
    db_deps.AsyncSessionLocal = original_session_factory
    setattr(db_deps, "redis_url", original_redis)
    setattr(auth_dependency, "redis", original_auth_redis)
    app.dependency_overrides.pop(db_deps.get_session, None)
    app.dependency_overrides.pop(db_deps.get_redis, None)


@pytest.fixture
def authenticated_client(client: TestClient, user: User) -> TestClient:
    response = client.post(
        "/auth/login",
        data={
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert response.status_code == 200, response.text
    assert client.cookies.get("session_id") is not None
    return client


@pytest.fixture
def logged_in_client(authenticated_client: TestClient) -> TestClient:
    return authenticated_client


@pytest.fixture
def authorized_client(authenticated_client: TestClient) -> TestClient:
    """Backward-compatible name for the authenticated test client."""
    return authenticated_client


@pytest.fixture
async def finance_user(db_session: AsyncSession) -> User:
    finance_email = f"finance-{uuid4().hex[:8]}@example.com"
    user = User(
        id=uuid4(),
        username=f"finance-{uuid4().hex[:8]}",
        email=finance_email,
        is_activated=True,
        hashed_password="test-hash",
        email_blind_index=get_blind_index(finance_email),
        is_totp_enabled=False,
    )
    wallet = Wallet(user_id=user.id)
    db_session.add(user)
    db_session.add(wallet)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> User:
    fresh_user = User(
        id=uuid4(),
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        is_activated=True,
        hashed_password=get_password_hash(TEST_USER_PASSWORD),
        email_blind_index=get_blind_index(TEST_USER_EMAIL),
    )
    db_session.add(fresh_user)
    db_session.add(Wallet(user_id=fresh_user.id))
    await db_session.commit()
    await db_session.refresh(fresh_user)
    return fresh_user


@pytest.fixture
async def wallet(db_session: AsyncSession, finance_user: User) -> Wallet:
    result = await db_session.get(Wallet, finance_user.id)
    assert result is not None
    return result


@pytest.fixture
def transaction_factory(wallet: Wallet):
    def factory(amount: Decimal = Decimal("10.00"), transaction_type: TransactionType = TransactionType.DEPOSIT) -> Transaction:
        return Transaction(wallet_id=wallet.user_id, amount=amount, type=transaction_type)
    return factory


@pytest.fixture
async def payment_operation_factory(finance_user: User, db_session: AsyncSession):
    async def factory(amount: Decimal = Decimal("10.00"), operation_type: PaymentOperationType = PaymentOperationType.DEPOSIT) -> PaymentOperation:
        operation = PaymentOperation(user_id=finance_user.id, amount=amount, type=operation_type)
        db_session.add(operation)
        await db_session.commit()
        await db_session.refresh(operation)
        return operation
    return factory


@pytest.fixture
def admin_context() -> CurrentUserContext:
    return CurrentUserContext(
        session_id="test-admin-session",
        user_id=uuid4(),
        username="test-admin",
        is_superuser=True,
        is_totp_enabled=False,
    )


@pytest.fixture
def override_admin(admin_context: CurrentUserContext):
    dependency = get_args(AdminUser)[1].dependency

    async def override() -> CurrentUserContext:
        return admin_context

    app.dependency_overrides[dependency] = override
    yield admin_context
    app.dependency_overrides.pop(dependency, None)
