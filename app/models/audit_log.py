from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    action = Column(
        String(100),
        nullable=False,
    )

    resource = Column(
        String(100),
        nullable=False,
    )

    resource_id = Column(
        Integer,
        nullable=True,
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
    )

    # Tamper-Evident Cryptographic Hash Chaining (TE-PQAC)
    previous_hash = Column(
        String(64),
        nullable=True,
    )

    current_hash = Column(
        String(64),
        nullable=True,
    )