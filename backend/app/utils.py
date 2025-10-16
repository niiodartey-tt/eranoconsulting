# backend/app/utils.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import schemas, crud
from app.db import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

# ✅ Single source of truth for JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_me_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_for_bcrypt(pw: str) -> str:
    """Ensure no ValueError for bcrypt (72 bytes max)"""
    safe_pw = pw.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return safe_pw


def hash_password(password: str) -> str:
    """Hash password safely (bcrypt has a 72-byte limit)"""
    safe_pw = _truncate_for_bcrypt(password)
    return pwd_context.hash(safe_pw)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    safe_pw = _truncate_for_bcrypt(plain_password)
    return pwd_context.verify(safe_pw, hashed_password)


def create_access_token(
    subject: str | int, email: str, role: str, expires_delta: Optional[timedelta] = None
):
    """Create JWT access token"""
    to_encode = {"sub": str(subject), "email": email, "role": role}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_refresh_expires_at():
    """Get refresh token expiration datetime"""
    return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)


def decode_token(token: str):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_db():
    """Database session dependency"""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Extract and verify current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # ✅ Use JWT_SECRET_KEY (same as token creation)
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("email") or payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError as e:
        print(f"JWT Error: {e}")  # Debug log
        raise credentials_exception

    user = await crud.get_user_by_email(db, email=email)

    if user is None:
        raise credentials_exception

    return user
