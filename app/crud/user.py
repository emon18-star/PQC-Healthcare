from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        password=user.password,
        role=user.role,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_users(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None

    user.username = user_data.username
    user.password = user_data.password
    user.role = user_data.role

    db.commit()
    db.refresh(user)

    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None

    db.delete(user)
    db.commit()

    return user