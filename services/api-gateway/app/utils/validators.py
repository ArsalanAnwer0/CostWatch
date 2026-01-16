"""
Input validation utilities for API Gateway
"""
from datetime import datetime
from typing import Optional
import re


def validate_aws_account_id(account_id: str) -> bool:
    """
    Validate AWS account ID format

    Args:
        account_id: AWS account ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not account_id:
        return False

    # AWS account IDs are 12-digit numbers
    return bool(re.match(r'^\d{12}$', account_id))


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string is in YYYY-MM-DD format

    Args:
        date_str: Date string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False


def validate_date_range(start_date: str, end_date: str) -> tuple[bool, Optional[str]]:
    """
    Validate date range is valid

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        tuple: (is_valid, error_message)
    """
    if not validate_date_format(start_date):
        return False, "Invalid start_date format. Use YYYY-MM-DD"

    if not validate_date_format(end_date):
        return False, "Invalid end_date format. Use YYYY-MM-DD"

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    if start > end:
        return False, "start_date must be before end_date"

    # Check if range is reasonable (not more than 1 year)
    days_diff = (end - start).days
    if days_diff > 365:
        return False, "Date range cannot exceed 365 days"

    return True, None


def validate_region(region: str) -> bool:
    """
    Validate AWS region format

    Args:
        region: AWS region to validate

    Returns:
        bool: True if valid, False otherwise
    """
    # Basic AWS region pattern: us-west-2, eu-central-1, etc.
    pattern = r'^[a-z]{2}-[a-z]+-\d{1}$'
    return bool(re.match(pattern, region))


def validate_resource_type(resource_type: str) -> bool:
    """
    Validate resource type is supported

    Args:
        resource_type: Resource type to validate

    Returns:
        bool: True if valid, False otherwise
    """
    valid_types = {
        'ec2', 'rds', 's3', 'ebs', 'lambda',
        'dynamodb', 'cloudwatch', 'vpc', 'elb'
    }
    return resource_type.lower() in valid_types


def sanitize_string(input_str: str, max_length: int = 255) -> str:
    """
    Sanitize string input

    Args:
        input_str: String to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized string
    """
    if not input_str:
        return ""

    # Remove null bytes
    sanitized = input_str.replace('\x00', '')

    # Truncate to max length
    sanitized = sanitized[:max_length]

    # Strip whitespace
    sanitized = sanitized.strip()

    return sanitized
