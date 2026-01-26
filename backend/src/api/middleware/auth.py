"""
Authentication middleware for the Advanced Todo application.
Handles JWT token validation and user authentication.
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTBearer(HTTPBearer):
    """
    Custom JWT Bearer authentication scheme.
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            token = credentials.credentials
            user_id = self.verify_jwt(token)
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            # Add user_id to request state for later use
            request.state.user_id = user_id
            return token
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authentication credentials were not provided."
            )

    def verify_jwt(self, jwt_token: str) -> Optional[str]:
        """
        Verify JWT token and return user ID if valid.

        Args:
            jwt_token: JWT token to verify

        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")

            # Check if token is expired
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
                return None

            return user_id
        except JWTError:
            logger.warning(f"Invalid JWT token: {jwt_token[:10]}...")
            return None


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token.

    Args:
        data: Data to encode in the token
        expires_delta: Expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire.timestamp()})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate hash for a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware function that intercepts requests and validates JWT tokens.

    Args:
        request: Incoming request
        call_next: Next middleware in the chain

    Returns:
        Response from the next middleware or an error response
    """
    # Skip authentication for public endpoints
    public_endpoints = ["/", "/health", "/docs", "/redoc", "/openapi.json"]

    if request.url.path in public_endpoints:
        response = await call_next(request)
        return response

    # For API endpoints, check for authentication
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]
        user_id = verify_jwt_token(token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Add user_id to request state for use in route handlers
        request.state.user_id = user_id

    response = await call_next(request)
    return response


def verify_jwt_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and return user ID if valid.

    Args:
        token: JWT token to verify

    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        # Check if token is expired
        exp_timestamp = payload.get("exp")
        if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
            return None

        return user_id
    except JWTError:
        logger.warning(f"Invalid JWT token received")
        return None