"""
Authentication Service
Handles user signup, signin, password hashing/verification, JWT token generation
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt
from sqlmodel import Session

from src.config import settings
# Don't import User model to avoid mapper binding issues


class AuthenticationError(Exception):
    """Raised when authentication fails"""

    pass


class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user with existing email"""

    pass


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def generate_jwt_token(user_id: str, email: str) -> tuple[str, datetime]:
    """
    Generate JWT token for user

    Args:
        user_id: User ID to include in token
        email: User email to include in token

    Returns:
        Tuple of (token string, expiration datetime)
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(days=settings.jwt_expiry_days)

    payload = {
        "user_id": user_id,
        "email": email,
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm
    )

    return token, expires_at


def create_user(session: Session, email: str, name: str, password: str):
    """
    Create a new user with hashed password

    Args:
        session: Database session
        email: User email (must be unique)
        name: User display name
        password: Plain text password (will be hashed)

    Returns:
        Created User object

    Raises:
        UserAlreadyExistsError: If email already exists
    """
    # Check if user already exists using direct SQL
    from sqlalchemy import text

    check_query = text("SELECT id FROM users WHERE email = :email LIMIT 1")
    existing = session.exec(check_query, params={"email": email}).first()
    if existing:
        raise UserAlreadyExistsError(f"User with email {email} already exists")

    # Create new user
    user_id = f"user_{uuid.uuid4().hex[:16]}"
    password_hash = hash_password(password)

    # Use direct SQL insert to avoid SQLModel metadata binding issues
    from sqlalchemy import text

    created = datetime.utcnow()

    # Insert user
    insert_query = text("""
        INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
        VALUES (:id, :email, :name, :password_hash, :created_at, :updated_at)
    """)

    session.exec(insert_query, params={
        "id": user_id,
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "created_at": created,
        "updated_at": created
    })

    session.commit()

    # Query the inserted user
    select_query = text("""
        SELECT id, email, name, password_hash, created_at, updated_at
        FROM users
        WHERE id = :id
    """)

    result = session.exec(select_query, params={"id": user_id}).first()

    # Return simple object instead of User model to avoid mapper issues
    class SimpleUser:
        def __init__(self, id, email, name, password_hash, created_at, updated_at):
            self.id = id
            self.email = email
            self.name = name
            self.password_hash = password_hash
            self.created_at = created_at
            self.updated_at = updated_at

    return SimpleUser(result[0], result[1], result[2], result[3], result[4], result[5])


def authenticate_user(session: Session, email: str, password: str):
    """
    Authenticate user with email and password

    Args:
        session: Database session
        email: User email
        password: Plain text password

    Returns:
        Authenticated User object

    Raises:
        AuthenticationError: If credentials are invalid
    """
    # Find user by email using direct SQL
    from sqlalchemy import text

    query = text("""
        SELECT id, email, name, password_hash, created_at, updated_at
        FROM users
        WHERE email = :email
        LIMIT 1
    """)

    result = session.exec(query, params={"email": email}).first()

    if not result:
        raise AuthenticationError("Invalid email or password")

    # Create simple user object from result
    class SimpleUser:
        def __init__(self, id, email, name, password_hash, created_at, updated_at):
            self.id = id
            self.email = email
            self.name = name
            self.password_hash = password_hash
            self.created_at = created_at
            self.updated_at = updated_at

    user = SimpleUser(
        result[0],  # id
        result[1],  # email
        result[2],  # name
        result[3],  # password_hash
        result[4],  # created_at
        result[5]   # updated_at
    )

    # Verify password
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    return user


def get_user_by_id(session: Session, user_id: str):
    """
    Get user by ID

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User object or None if not found
    """
    from sqlalchemy import text

    query = text("""
        SELECT id, email, name, password_hash, created_at, updated_at
        FROM users
        WHERE id = :user_id
        LIMIT 1
    """)

    result = session.exec(query, params={"user_id": user_id}).first()

    if not result:
        return None

    class SimpleUser:
        def __init__(self, id, email, name, password_hash, created_at, updated_at):
            self.id = id
            self.email = email
            self.name = name
            self.password_hash = password_hash
            self.created_at = created_at
            self.updated_at = updated_at

    return SimpleUser(
        result[0],
        result[1],
        result[2],
        result[3],
        result[4],
        result[5]
    )
