from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    """User model"""
    user_id: str
    email: EmailStr
    name: str
    role: str
    account_ids: List[str]
    created_at: Optional[datetime] = None
    is_active: bool = True

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    name: str
    role: str = "user"
    account_ids: List[str] = []

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str