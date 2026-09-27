from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Counts requests per client IP in memory. That's fine for our single container;
# running several instances would need a shared store such as Redis.
limiter = Limiter(key_func=get_remote_address)

UPLOAD_LIMIT = "10/minute"
SHARE_INFO_LIMIT = "60/minute"
# Also caps password guessing, since every attempt goes through the download endpoint.
DOWNLOAD_LIMIT = "10/minute"


def rate_limit_exceeded(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        {"detail": "Too many requests. Please wait a minute and try again."},
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": "60"},
    )
