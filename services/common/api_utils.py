"""
API Response and Error Handling Utilities
Provides standardized response formatting and error handling for all services
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    """Enumeration of common error codes"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


def create_success_response(data: Any = None, message: str = "Success", **kwargs) -> Dict[str, Any]:
    """
    Create a standardized success response

    Args:
        data: Response data
        message: Success message
        **kwargs: Additional fields to include in the response

    Returns:
        Dict: Standardized success response
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }

    # Add any additional fields
    response.update(kwargs)

    return response


def create_error_response(error: str, details: Optional[Dict] = None, code: Optional[str] = None, message: str = "Error occurred") -> Dict[str, Any]:
    """
    Create a standardized error response

    Args:
        error: Error message
        details: Additional error details
        code: Error code
        message: User-friendly message

    Returns:
        Dict: Standardized error response
    """
    response = {
        "success": False,
        "message": message,
        "error": error,
        "details": details,
        "code": code
    }

    return response


def handle_api_exception(exc: Exception, error_code: str = ErrorCode.INTERNAL_ERROR, message: str = "An unexpected error occurred"):
    """
    Handle API exceptions and return standardized error response

    Args:
        exc: Exception object
        error_code: Error code to return
        message: User-friendly error message

    Returns:
        Dict: Standardized error response
    """
    logger.error(f"{error_code}: {str(exc)}", exc_info=True)

    return create_error_response(
        error=str(exc),
        code=error_code,
        message=message,
        details={"type": type(exc).__name__}
    )


def create_http_exception(
    status_code: int,
    detail: str,
    headers: Optional[Dict[str, str]] = None
) -> HTTPException:
    """
    Create a standardized HTTP exception

    Args:
        status_code: HTTP status code
        detail: Error detail
        headers: Optional headers

    Returns:
        HTTPException: FastAPI HTTP exception
    """
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


def validation_error_response(errors: list) -> Dict[str, Any]:
    """
    Create a standardized validation error response

    Args:
        errors: List of validation errors

    Returns:
        Dict: Standardized validation error response
    """
    return create_error_response(
        error="Validation failed",
        code=ErrorCode.VALIDATION_ERROR,
        message="One or more validation errors occurred",
        details={"errors": errors}
    )


def not_found_response(item_type: str, item_id: Any) -> Dict[str, Any]:
    """
    Create a standardized not found response

    Args:
        item_type: Type of item not found
        item_id: ID of item not found

    Returns:
        Dict: Standardized not found response
    """
    return create_error_response(
        error=f"{item_type} not found",
        code=ErrorCode.NOT_FOUND,
        message=f"The {item_type.lower()} with ID {item_id} was not found",
        details={"item_type": item_type, "item_id": item_id}
    )


def unauthorized_response(message: str = "Unauthorized access") -> Dict[str, Any]:
    """
    Create a standardized unauthorized response

    Args:
        message: Unauthorized message

    Returns:
        Dict: Standardized unauthorized response
    """
    return create_error_response(
        error="Unauthorized",
        code=ErrorCode.UNAUTHORIZED,
        message=message
    )


def forbidden_response(message: str = "Forbidden access") -> Dict[str, Any]:
    """
    Create a standardized forbidden response

    Args:
        message: Forbidden message

    Returns:
        Dict: Standardized forbidden response
    """
    return create_error_response(
        error="Forbidden",
        code=ErrorCode.FORBIDDEN,
        message=message
    )


def conflict_response(message: str = "Conflict occurred") -> Dict[str, Any]:
    """
    Create a standardized conflict response

    Args:
        message: Conflict message

    Returns:
        Dict: Standardized conflict response
    """
    return create_error_response(
        error="Conflict",
        code=ErrorCode.CONFLICT,
        message=message
    )


def service_unavailable_response(message: str = "Service temporarily unavailable") -> Dict[str, Any]:
    """
    Create a standardized service unavailable response

    Args:
        message: Service unavailable message

    Returns:
        Dict: Standardized service unavailable response
    """
    return create_error_response(
        error="Service Unavailable",
        code=ErrorCode.SERVICE_UNAVAILABLE,
        message=message
    )


# Custom exception classes
class TodoException(Exception):
    """Base exception class for todo application"""

    def __init__(self, message: str, code: str = ErrorCode.INTERNAL_ERROR, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ValidationError(TodoException):
    """Exception raised for validation errors"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)


class NotFoundException(TodoException):
    """Exception raised when an item is not found"""

    def __init__(self, item_type: str, item_id: Any):
        message = f"{item_type} with ID {item_id} not found"
        details = {"item_type": item_type, "item_id": item_id}
        super().__init__(message, ErrorCode.NOT_FOUND, details)


class UnauthorizedException(TodoException):
    """Exception raised for unauthorized access"""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, ErrorCode.UNAUTHORIZED)


class ForbiddenException(TodoException):
    """Exception raised for forbidden access"""

    def __init__(self, message: str = "Forbidden access"):
        super().__init__(message, ErrorCode.FORBIDDEN)


class ConflictException(TodoException):
    """Exception raised for conflicts"""

    def __init__(self, message: str = "Conflict occurred"):
        super().__init__(message, ErrorCode.CONFLICT)


def handle_validation_error(errors: list) -> HTTPException:
    """
    Convert validation errors to HTTP exception

    Args:
        errors: List of validation errors

    Returns:
        HTTPException: FastAPI HTTP exception
    """
    error_detail = validation_error_response(errors)
    return create_http_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=error_detail
    )


def handle_not_found(item_type: str, item_id: Any) -> HTTPException:
    """
    Convert not found to HTTP exception

    Args:
        item_type: Type of item not found
        item_id: ID of item not found

    Returns:
        HTTPException: FastAPI HTTP exception
    """
    error_detail = not_found_response(item_type, item_id)
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=error_detail
    )


def handle_unauthorized(message: str = "Unauthorized") -> HTTPException:
    """
    Convert unauthorized to HTTP exception

    Args:
        message: Unauthorized message

    Returns:
        HTTPException: FastAPI HTTP exception
    """
    error_detail = unauthorized_response(message)
    return create_http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_detail
    )


def handle_forbidden(message: str = "Forbidden") -> HTTPException:
    """
    Convert forbidden to HTTP exception

    Args:
        message: Forbidden message

    Returns:
        HTTPException: FastAPI HTTP exception
    """
    error_detail = forbidden_response(message)
    return create_http_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=error_detail
    )


# Example usage
if __name__ == "__main__":
    # Example of creating different types of responses
    success_resp = create_success_response(
        data={"task_id": 123},
        message="Task created successfully"
    )
    print("Success response:", success_resp)

    error_resp = create_error_response(
        error="Invalid input",
        code=ErrorCode.VALIDATION_ERROR,
        message="The provided input was invalid",
        details={"field": "title", "reason": "required"}
    )
    print("Error response:", error_resp)

    # Example of using custom exceptions
    try:
        raise ValidationError("Title is required", details={"field": "title"})
    except ValidationError as e:
        print(f"Caught validation error: {e.message}, code: {e.code}")