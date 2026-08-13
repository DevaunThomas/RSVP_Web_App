from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Dict, Optional
from flask import g, jsonify, request
import jwt

from config import Config


def generate_token(user_id: int, role: str, name: str, email: str) -> str:
    """Generates a JWT token for a user with a 24-hour expiration."""
    payload = {
        "user_id": user_id,
        "role": role,
        "name": name,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def token_required(f):
    """Decorator to enforce valid JWT authentication on routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization token required"}), 401

        token = auth_header.split(" ")[1]
        payload = decode_token(token)

        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        g.current_user = payload
        return f(*args, **kwargs)

    return decorated


def organizer_required(f):
    """Decorator to enforce that the authenticated user has the 'organizer' role."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if g.current_user.get("role") != "organizer":
            return jsonify({"error": "Organizer access required"}), 403

        return f(*args, **kwargs)

    return decorated
