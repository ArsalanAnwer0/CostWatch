"""
Standardized API response utilities
"""
from typing import Any, Dict, Optional
from datetime import datetime


def success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Create a standardized success response

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code

    Returns:
        dict: Formatted response
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

    if message:
        response["message"] = message

    return response


def error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> tuple[Dict[str, Any], int]:
    """
    Create a standardized error response

    Args:
        message: Error message
        error_code: Optional error code for client handling
        details: Optional additional error details
        status_code: HTTP status code

    Returns:
        tuple: (response dict, status code)
    """
    response = {
        "success": False,
        "error": {
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

    if error_code:
        response["error"]["code"] = error_code

    if details:
        response["error"]["details"] = details

    return response, status_code


def validation_error_response(
    field: str,
    message: str,
    value: Optional[Any] = None
) -> tuple[Dict[str, Any], int]:
    """
    Create a validation error response

    Args:
        field: Field name that failed validation
        message: Validation error message
        value: Optional invalid value

    Returns:
        tuple: (response dict, status code)
    """
    details = {
        "field": field,
        "message": message
    }

    if value is not None:
        details["value"] = str(value)

    return error_response(
        message=f"Validation failed for field: {field}",
        error_code="VALIDATION_ERROR",
        details=details,
        status_code=422
    )


def not_found_response(
    resource: str,
    resource_id: Optional[str] = None
) -> tuple[Dict[str, Any], int]:
    """
    Create a not found error response

    Args:
        resource: Resource type (e.g., "account", "report")
        resource_id: Optional resource identifier

    Returns:
        tuple: (response dict, status code)
    """
    message = f"{resource.capitalize()} not found"
    if resource_id:
        message += f": {resource_id}"

    return error_response(
        message=message,
        error_code="NOT_FOUND",
        status_code=404
    )


def unauthorized_response(
    message: str = "Unauthorized access"
) -> tuple[Dict[str, Any], int]:
    """
    Create an unauthorized error response

    Args:
        message: Error message

    Returns:
        tuple: (response dict, status code)
    """
    return error_response(
        message=message,
        error_code="UNAUTHORIZED",
        status_code=401
    )


def rate_limit_response(
    retry_after: Optional[int] = None
) -> tuple[Dict[str, Any], int]:
    """
    Create a rate limit error response

    Args:
        retry_after: Seconds until retry is allowed

    Returns:
        tuple: (response dict, status code)
    """
    details = {}
    if retry_after:
        details["retry_after"] = retry_after

    return error_response(
        message="Rate limit exceeded. Please try again later.",
        error_code="RATE_LIMIT_EXCEEDED",
        details=details if details else None,
        status_code=429
    )


def server_error_response(
    message: str = "An internal server error occurred"
) -> tuple[Dict[str, Any], int]:
    """
    Create a server error response

    Args:
        message: Error message

    Returns:
        tuple: (response dict, status code)
    """
    return error_response(
        message=message,
        error_code="INTERNAL_SERVER_ERROR",
        status_code=500
    )
