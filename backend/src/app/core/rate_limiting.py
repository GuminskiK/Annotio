from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.extension import _rate_limit_exceeded_handler
from fastapi import Request, Response

limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])

async def custom_rate_limit_handler(request: Request, exc: Exception) -> Response:
    return await _rate_limit_exceeded_handler(request, exc)  # type: ignore
