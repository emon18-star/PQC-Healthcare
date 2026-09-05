from app.core.key_manager import create_user_keypair
from app.core.security import hash_password

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate



from app.core.security import hash_password
from app.core.key_manager import create_user_keypair

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate):

    public_key = None
    private_key = None
    key_nonce = None

    if user.role.lower() == "doctor":
        public_key, private_key, key_nonce = create_user_keypair()

    db_user = User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role,
        public_key=public_key,
        private_key=private_key,
        key_nonce=key_nonce,
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
    user.password = hash_password(user_data.password)
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

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()