"""
Pydantic schemas for API error responses
Standardized error formats for client consumption
"""

from pydantic import BaseModel
from typing import List, Any, Optional


class ErrorResponse(BaseModel):
    """Generic error response for 4xx and 5xx errors"""

    detail: str

    class Config:
        json_schema_extra = {"example": {"detail": "Error message"}}


class ValidationErrorDetail(BaseModel):
    """Individual validation error detail"""

    loc: List[str]  # Field path, e.g., ["body", "title"]
    msg: str  # Error message
    type: str  # Error type, e.g., "value_error.any_str.min_length"

    class Config:
        json_schema_extra = {
            "example": {
                "loc": ["body", "title"],
                "msg": "ensure this value has at least 1 characters",
                "type": "value_error.any_str.min_length",
            }
        }


class ValidationErrorResponse(BaseModel):
    """Validation error response for 422 Unprocessable Entity"""

    detail: List[ValidationErrorDetail]

    class Config:
        json_schema_extra = {
            "example": {
                "detail": [
                    {
                        "loc": ["body", "title"],
                        "msg": "ensure this value has at least 1 characters",
                        "type": "value_error.any_str.min_length",
                    }
                ]
            }
        }
