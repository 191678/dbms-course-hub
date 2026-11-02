from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import bcrypt as bcrypt_lib
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt_lib.hashpw(password_bytes, bcrypt_lib.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt_lib.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    except Exception:
        return None


def get_current_user_id(token: str) -> Optional[int]:
    payload = decode_access_token(token)
    if payload:
        return payload.get("user_id")
    return None


def get_current_user_role(token: str) -> Optional[str]:
    payload = decode_access_token(token)
    if payload:
        return payload.get("role")
    return None


def is_token_expired(token: str) -> bool:
    payload = decode_access_token(token)
    if not payload:
        return True
    exp = payload.get("exp")
    if exp:
        return datetime.utcnow() > datetime.utcfromtimestamp(exp)
    return True
