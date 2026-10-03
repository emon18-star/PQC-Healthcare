from datetime import datetime, timedelta
import os
from jose import jwt, JWTError
from fastapi import HTTPException

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.crud.user import get_user_by_username
from fastapi import Depends

from dotenv import load_dotenv
from jose import jwt

load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def create_access_token(data: dict):
    """
    Create a JWT access token.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt

def verify_access_token(token: str):
    """
    Verify a JWT access token and return its payload.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

import time

_USER_CACHE: dict = {}
_USER_CACHE_TTL = 300  # 5 minutes


class CachedUser:
    def __init__(self, id, username, role, public_key, private_key, key_nonce):
        self.id = id
        self.username = username
        self.role = role
        self.public_key = public_key
        self.private_key = private_key
        self.key_nonce = key_nonce


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Return the currently authenticated user with in-memory caching.
    """
    payload = verify_access_token(token)

    username = payload.get("sub")

    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    now = time.time()
    cached = _USER_CACHE.get(username)
    if cached and (now - cached[1] < _USER_CACHE_TTL):
        return cached[0]

    user = get_user_by_username(db, username)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    cached_user = CachedUser(
        id=user.id,
        username=user.username,
        role=user.role,
        public_key=user.public_key,
        private_key=user.private_key,
        key_nonce=user.key_nonce,
    )
    _USER_CACHE[username] = (cached_user, now)

    return cached_user


def require_role(required_role: str):
    """
    Ensure the current user has the required role (supports comma-separated roles).
    """
    allowed_roles = [r.strip().lower() for r in required_role.split(",")]

    def role_checker(
        current_user=Depends(get_current_user)
    ):
        if current_user.role.lower() not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return role_checker    