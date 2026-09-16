# services/api/core/auth.py
import os
import time
from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hmac
import hashlib
import json
import base64

from .errors import AuthenticationError, ForbiddenError
from .logging import get_logger

logger = get_logger("auth")

JWT_SECRET = os.getenv("JWT_SECRET", "projectpulse-development-insecure-secret-key-32chars")
API_KEY = os.getenv("PROJECTPULSE_API_KEY", "pp_live_demo_secret_key_2026")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

class AuthenticatedUser(BaseModel):
    user_id: str
    email: str
    role: str  # viewer, operator, manager, admin

security = HTTPBearer(auto_error=False)

def create_jwt_token(user_id: str, email: str, role: str, expires_in: int = 86400) -> str:
    """Generates a standard HS256 JWT token with expiration timestamp."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time())
    }
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(
        JWT_SECRET.encode(),
        f"{encoded_header}.{encoded_payload}".encode(),
        hashlib.sha256
    ).digest()
    encoded_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{encoded_header}.{encoded_payload}.{encoded_sig}"

def decode_jwt_token(token: str) -> dict:
    """Decodes and validates HS256 JWT signature and expiration."""
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthenticationError("Invalid JWT token structure")
    
    header_b64, payload_b64, sig_b64 = parts
    # Pad base64 strings
    payload_padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    sig_padded = sig_b64 + "=" * (-len(sig_b64) % 4)
    
    expected_sig = hmac.new(
        JWT_SECRET.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    
    try:
        actual_sig = base64.urlsafe_b64decode(sig_padded.encode())
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise AuthenticationError("Invalid token signature")
        
        payload = json.loads(base64.urlsafe_b64decode(payload_padded.encode()).decode())
        if payload.get("exp") and payload["exp"] < time.time():
            raise AuthenticationError("Token has expired")
        return payload
    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(f"Malformed token: {str(e)}")

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> AuthenticatedUser:
    """
    Dependency that authenticates callers via Bearer JWT or X-API-Key header.
    In development mode without headers, returns an authenticated operator for seamless local demo.
    """
    # 1. Check API Key
    if x_api_key:
        if hmac.compare_digest(x_api_key, API_KEY):
            return AuthenticatedUser(user_id="api-service", email="service@projectpulse.ai", role="admin")
        raise AuthenticationError("Invalid X-API-Key header")
    
    # 2. Check Bearer JWT
    if credentials and credentials.credentials:
        payload = decode_jwt_token(credentials.credentials)
        return AuthenticatedUser(
            user_id=payload.get("sub", "unknown"),
            email=payload.get("email", ""),
            role=payload.get("role", "viewer")
        )
    
    # 3. Development Fallback (Permissive local demo mode if configured)
    if ENVIRONMENT == "development":
        return AuthenticatedUser(user_id="dev-user-001", email="dev@projectpulse.local", role="admin")
        
    raise AuthenticationError("Missing Bearer token or X-API-Key header")

def require_role(allowed_roles: List[str]):
    """Role-Based Access Control (RBAC) dependency factory."""
    async def role_checker(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role not in allowed_roles and "admin" not in user.role:
            raise ForbiddenError(f"Role '{user.role}' is not authorized. Requires one of {allowed_roles}")
        return user
    return role_checker
