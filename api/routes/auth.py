"""
Authentication routes for the API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.auth import authenticate_user, hash_password
from database.models import User, UserDailyLogin

router = APIRouter()
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Decode JWT and return current user."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        init_db()
        db = get_db()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    init_db()
    db = get_db()

    user = authenticate_user(db, request.email, request.password)

    if not user:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )

    # Update last login
    user.last_login = datetime.utcnow()

    # Track daily login for usage analytics (one record per user per day)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_login = db.query(UserDailyLogin).filter(
        UserDailyLogin.user_id == user.id,
        UserDailyLogin.login_date == today
    ).first()
    if not existing_login:
        daily_login = UserDailyLogin(user_id=user.id, login_date=today)
        db.add(daily_login)

    db.commit()

    # Create token
    access_token = create_access_token(data={"user_id": user.id, "role": user.role})

    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }

    db.close()
    return response


@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest):
    """Register new user and return JWT token."""
    init_db()
    db = get_db()

    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=request.email,
        username=request.email,  # Use email as username
        password_hash=hash_password(request.password),
        role="user",
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create token
    access_token = create_access_token(data={"user_id": user.id, "role": user.role})

    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }

    db.close()
    return response


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role
    }
