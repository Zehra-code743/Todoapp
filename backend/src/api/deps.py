"""
Dependency injection for FastAPI endpoints
Provides reusable dependencies for authentication and database access
"""

from typing import Annotated
from fastapi import Depends, Header, HTTPException, status

from src.middleware.jwt_auth import extract_user_id_from_token


def get_current_user(authorization: str = Header(None)) -> str:
    """
    Dependency to get current authenticated user ID from JWT token

    Args:
        authorization: Authorization header with JWT token

    Returns:
        User ID string extracted from JWT token

    Raises:
        HTTPException: 401 if token is missing or invalid

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            return {"user_id": user_id}
    """
    return extract_user_id_from_token(authorization)


def verify_user_id_match(
    path_user_id: str,
    current_user: Annotated[str, Depends(get_current_user)],
) -> str:
    """
    Verify that URL path user_id matches authenticated user_id from JWT

    Args:
        path_user_id: User ID from URL path parameter
        current_user: User ID from JWT token (via dependency injection)

    Returns:
        User ID if verification passes

    Raises:
        HTTPException: 403 if user_id mismatch

    Usage:
        @app.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: str,
            verified_user_id: str = Depends(lambda user_id=user_id: verify_user_id_match(user_id, ...))
        ):
            ...
    """
    if path_user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )
    return current_user


# Type alias for dependency injection
CurrentUser = Annotated[str, Depends(get_current_user)]
