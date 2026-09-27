from fastapi import Request, Response
from slowapi import Limiter
from slowapi.extension import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])

async def custom_rate_limit_handler(request: Request, exc: Exception) -> Response:
    return await _rate_limit_exceeded_handler(request, exc)  # type: ignore
