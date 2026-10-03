from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func

from app.database.database import Base


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    doctor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    record_id = Column(
        Integer,
        ForeignKey("medical_records.id"),
        nullable=False,
    )

    reason = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        default="PENDING",
    )

    approved_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    requested_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Zero-Payload-Decryption Delegated PQC Parameters
    delegated_kem_ciphertext = Column(
        Text,
        nullable=True,
    )

    delegated_encrypted_aes_key = Column(
        Text,
        nullable=True,
    )

    delegated_aes_key_nonce = Column(
        Text,
        nullable=True,
    )