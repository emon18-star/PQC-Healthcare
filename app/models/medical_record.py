from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)

from app.database.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
    )

    # Entire encrypted medical record (JSON string)
    encrypted_record = Column(
        Text,
        nullable=False,
    )

    # ML-KEM ciphertext
    kem_ciphertext = Column(
        Text,
        nullable=False,
    )

    # AES session key encrypted using the shared secret
    encrypted_aes_key = Column(
        Text,
        nullable=False,
    )

    # Nonce used when encrypting the AES session key
    aes_key_nonce = Column(
        Text,
        nullable=False,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )