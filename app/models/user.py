from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    public_key = Column(Text, nullable=True)

    private_key = Column(Text, nullable=True)

    key_nonce = Column(Text, nullable=True)