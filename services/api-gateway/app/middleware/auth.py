from fastapi import Depends
from app.routes.auth import verify_token


async def get_current_user(email: str = Depends(verify_token)):
    """Get current authenticated user from JWT token."""
    return email
