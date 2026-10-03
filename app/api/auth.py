from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.crud.user import get_user_by_username
from app.core.security import verify_password
from app.core.auth import create_access_token

from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account (doctor, admin, or patient).
    Generates a post-quantum ML-KEM-768 keypair automatically for doctor accounts.
    """
    existing = get_user_by_username(db, user.username.strip())
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Username '{user.username}' is already registered. Please choose another."
        )

    # Public registration is available for Doctors and Admins
    role = (user.role or "doctor").strip().lower()
    if role not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Registration is only allowed for 'doctor' and 'admin' accounts."
        )
    user.role = role

    return create_user(db, user)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT bearer token.
    Supports both clean JSON payloads and URL-encoded form data.
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="Username and password are required"
        )

    db_user = get_user_by_username(db, username)

    if db_user is None or not verify_password(password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={
            "sub": db_user.username,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": db_user.username,
        "role": db_user.role
    }