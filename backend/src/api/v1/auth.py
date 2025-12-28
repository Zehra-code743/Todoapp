"""
Authentication API Endpoints
Handles user signup, signin, and signout
"""

from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlmodel import Session

from src.db import get_session
from src.schemas.auth_schemas import (
    SignUpRequest,
    SignInRequest,
    AuthResponse,
    SignOutResponse,
)
from src.services.auth_service import (
    create_user,
    authenticate_user,
    generate_jwt_token,
    UserAlreadyExistsError,
    AuthenticationError,
)

router = APIRouter()


@router.post("/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest, session: Session = Depends(get_session)):
    """
    Create new user account

    - **email**: Valid email address (must be unique)
    - **name**: Display name (2-100 characters)
    - **password**: Password (minimum 8 characters)

    Returns user info and JWT token for immediate signin
    """
    try:
        # Create user
        user = create_user(
            session=session,
            email=request.email,
            name=request.name,
            password=request.password,
        )

        # Generate JWT token
        token, expires_at = generate_jwt_token(user.id, user.email)

        return AuthResponse(
            user={"id": user.id, "email": user.email, "name": user.name},
            token=token,
            expires_at=expires_at.isoformat() + "Z",
        )

    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


@router.post("/auth/signin", response_model=AuthResponse)
async def signin(request: SignInRequest, session: Session = Depends(get_session)):
    """
    Sign in with email and password

    - **email**: User's email address
    - **password**: User's password

    Returns user info and JWT token
    """
    try:
        # Authenticate user
        user = authenticate_user(
            session=session, email=request.email, password=request.password
        )

        # Generate JWT token
        token, expires_at = generate_jwt_token(user.id, user.email)

        return AuthResponse(
            user={"id": user.id, "email": user.email, "name": user.name},
            token=token,
            expires_at=expires_at.isoformat() + "Z",
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sign in: {str(e)}",
        )


@router.post("/auth/signout", response_model=SignOutResponse)
async def signout():
    """
    Sign out user

    This endpoint invalidates the user's session.
    Frontend should clear the JWT token from cookies/storage.

    Note: Since JWT is stateless, actual invalidation happens client-side.
    For production, consider using token blacklist or refresh tokens.
    """
    return SignOutResponse(message="Signed out successfully")
