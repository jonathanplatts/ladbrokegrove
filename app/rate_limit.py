from fastapi import Request, Depends

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth import verify_token


limiter = Limiter(key_func=get_remote_address)


def get_user_key(request: Request, user_data: dict = Depends(verify_token)):
    """Return user ID from JWT for rate-limiting, fallback to IP if unauthenticated."""
    if isinstance(user_data, dict) and "sub" in user_data:
        return user_data["sub"] if user_data else get_remote_address(request)
    else:
        return get_remote_address(request)
