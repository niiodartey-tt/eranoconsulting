# backend/app/utils.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
import secrets

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_me_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_for_bcrypt(pw: str) -> str:
    # Ensure no ValueError for bcrypt (72 bytes max)
    safe_pw = pw.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return safe_pw


def hash_password(password: str) -> str:
    return pwd_context.hash(password)
    """Hash password safely (bcrypt has a 72-byte limit)."""
    # Truncate to 72 bytes to prevent ValueError
    safe_pw = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(safe_pw)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | int, email: str, role: str, expires_delta: Optional[timedelta] = None
):
    to_encode = {"sub": str(subject), "email": email, "role": role}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_refresh_expires_at():
    return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
