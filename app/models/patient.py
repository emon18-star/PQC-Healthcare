from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey

from app.database.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(150), nullable=False)

    date_of_birth = Column(Date, nullable=False)

    gender = Column(String(20), nullable=False)

    blood_group = Column(String(10), nullable=False)

    phone = Column(String(20), nullable=False)

    email = Column(String(100), nullable=True)

    address = Column(String(255), nullable=True)

    emergency_contact = Column(String(100), nullable=True)

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )