import asyncio
import os
import shutil
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.deps.dbs import db_session, redis_client


def check_disk(min_free_percent: float = 10.0) -> tuple[bool, dict]:
    total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
    free_pct = round(free / total * 100, 2)

    return free_pct >= min_free_percent, {
        "free_percent": free_pct,
    }


async def check_db(
    session: AsyncSession,
    timeout: int = 3,
) -> tuple[bool, Any]:
    try:
        await asyncio.wait_for(
            session.execute(text("SELECT 1")),
            timeout=timeout,
        )
        return True, None
    except Exception as exc:
        return False, str(exc)


async def check_redis(
    session: redis_client,
    timeout: int = 3,
) -> tuple[bool, Any]:
    try:
        await asyncio.wait_for(session.ping(), timeout=timeout)
        return True, None
    except Exception as exc:
        return False, str(exc)