from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@limiter.request_filter
def exempt_preflight_requests() -> bool:
    """Prevents CORS preflight requests from using API limits."""
    return request.method == "OPTIONS"