from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.models.user import User
from app.core.auth import get_current_user, require_role

from app.database.session import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.crud.user import (
    create_user,
    get_users,
    get_user_by_id,
    update_user,
    delete_user,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user)

@router.get("/", response_model=list[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return get_users(db)

@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user



@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)

    if user is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

from fastapi import HTTPException


@router.put("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)
):
    updated_user = update_user(db, user_id, user)

    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return updated_user

@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    deleted_user = delete_user(db, user_id)

    if deleted_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully"
    }
