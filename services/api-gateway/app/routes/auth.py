from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from typing import Dict, Optional, Any
import jwt
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
import re

router = APIRouter()
security = HTTPBearer()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# Helper functions for password hashing
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

# Mock user database (replace with real database in production)
MOCK_USERS = {
    "admin@costwatch.com": {
        "id": 1,
        "email": "admin@costwatch.com",
        "full_name": "Admin User",
        "company": "CostWatch",
        "hashed_password": hash_password("AdminPass123"),  # Properly hashed password
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
    # Authenticate user with proper password verification
    user = MOCK_USERS.get(user_credentials.email)
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
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
    """Register new user with strong password requirements."""
    if user_data.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Register user with properly hashed password
    MOCK_USERS[user_data.email] = {
        "id": len(MOCK_USERS) + 1,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "company": user_data.company,
        "hashed_password": hash_password(user_data.password),
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