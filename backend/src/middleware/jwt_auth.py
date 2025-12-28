"""
JWT Authentication Middleware
Validates JWT tokens issued by Better Auth on the frontend
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Header
from jose import JWTError, jwt

from src.config import settings


def verify_jwt_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Verify JWT token from Authorization header and extract payload

    Args:
        authorization: Authorization header value (format: "Bearer <token>")

    Returns:
        Dictionary with decoded JWT payload (user_id, email, exp, iat)

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    try:
        # Verify and decode JWT token
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
        )

        # Ensure required fields are present
        if "user_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing user_id",
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_id_from_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract user_id from JWT token

    Args:
        authorization: Authorization header value

    Returns:
        User ID string from JWT payload

    Raises:
        HTTPException: 401 if token is invalid
    """
    payload = verify_jwt_token(authorization)
    return payload["user_id"]
