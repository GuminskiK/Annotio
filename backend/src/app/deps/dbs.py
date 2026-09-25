from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import from_url, Redis

from src.app.core.config import settings
from typing import Annotated
from fastapi import Depends
import redis.asyncio as redis

class DBDependency:
    def __init__(self, database_url, redis_url):
        self.engine = create_async_engine(
            database_url, future=True, echo=False
        )
        self.redis_url = from_url(redis_url, decode_responses=True)
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.AsyncSessionLocal() as session:
            yield session

    def get_redis(self) -> Redis:
        return self.redis_url
    
db_deps = DBDependency(database_url=settings.DATABASE_URL, redis_url=settings.REDIS_URL)

db_session = Annotated[AsyncSession, Depends(db_deps.get_session)]
redis_client = Annotated[redis.Redis, Depends(db_deps.get_redis)]
redis_pure = db_deps.get_redis()