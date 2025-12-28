"""
Authentication request/response schemas
"""

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    """Sign up request body"""

    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=2, max_length=100, description="User display name")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "password": "securepassword123",
            }
        }


class SignInRequest(BaseModel):
    """Sign in request body"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }


class AuthResponse(BaseModel):
    """Authentication response with user info and token"""

    user: dict = Field(..., description="User information")
    token: str = Field(..., description="JWT access token")
    expires_at: str = Field(..., description="Token expiration timestamp (ISO 8601)")

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "user_abc123",
                    "email": "user@example.com",
                    "name": "John Doe",
                },
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_at": "2025-01-02T10:30:00Z",
            }
        }


class SignOutResponse(BaseModel):
    """Sign out response"""

    message: str = Field(default="Signed out successfully")

    class Config:
        json_schema_extra = {"example": {"message": "Signed out successfully"}}
