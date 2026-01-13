from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional, Any
import jwt
import os
from datetime import datetime, timedelta

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# Mock user database (replace with real database in production)
MOCK_USERS = {
    "admin@costwatch.com": {
        "id": 1,
        "email": "admin@costwatch.com",
        "full_name": "Admin User",
        "company": "CostWatch",
        "hashed_password": "hashed_admin_password",  # In real app, use proper hashing
        "is_active": True
    }
}

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def bypass_auth_for_testing():
    """Bypass authentication for testing purposes."""
    return "test-user@costwatch.com"

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin) -> Token:
    """Authenticate user and return access token."""
    # Mock authentication (replace with real authentication)
    user = MOCK_USERS.get(user_credentials.email)
    if not user or user["hashed_password"] != f"hashed_{user_credentials.password}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/register", response_model=Dict[str, str])
async def register(user_data: UserRegister) -> Dict[str, str]:
    """Register new user."""
    if user_data.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Mock user registration (replace with real database operations)
    MOCK_USERS[user_data.email] = {
        "id": len(MOCK_USERS) + 1,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "company": user_data.company,
        "hashed_password": f"hashed_{user_data.password}",  # Use proper hashing
        "is_active": True
    }
    
    return {"message": "User registered successfully", "email": user_data.email}

@router.get("/me")
async def get_current_user(current_user_email: str = Depends(verify_token)) -> Dict[str, Any]:
    """Get current user information."""
    user = MOCK_USERS.get(current_user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't return password
    user_info = user.copy()
    user_info.pop("hashed_password", None)
    return user_info

@router.post("/logout")
async def logout(current_user_email: str = Depends(verify_token)) -> Dict[str, str]:
    """Logout user (in real app, you'd invalidate the token)."""
    return {"message": "Successfully logged out"}