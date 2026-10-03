import base64
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.access_request import AccessRequest
from app.models.medical_record import MedicalRecord
from app.models.user import User
from app.crud.audit_log import log_action
from app.core.mediator import Mediator
from app.core.key_manager import decrypt_private_key


def create_access_request(
    db: Session,
    doctor_id: int,
    record_id: int,
    reason: str,
):
    # Verify the record exists
    record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )

    if record is None:
        return None

    # Prevent duplicate pending requests
    existing = (
        db.query(AccessRequest)
        .filter(
            AccessRequest.doctor_id == doctor_id,
            AccessRequest.record_id == record_id,
            AccessRequest.status == "PENDING",
        )
        .first()
    )

    if existing:
        return existing

    request = AccessRequest(
        doctor_id=doctor_id,
        record_id=record_id,
        reason=reason,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    log_action(
        db=db,
        user_id=doctor_id,
        action="REQUEST_ACCESS",
        resource="MedicalRecord",
        resource_id=record_id,
    )

    return request


def get_pending_requests(db: Session):
    return (
        db.query(AccessRequest)
        .filter(AccessRequest.status == "PENDING")
        .order_by(AccessRequest.requested_at.desc())
        .all()
    )


def get_all_requests(db: Session, skip: int = 0, limit: int = 50):
    return (
        db.query(AccessRequest)
        .order_by(AccessRequest.requested_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def approve_request(
    db: Session,
    request_id: int,
    admin_id: int,
):
    request = (
        db.query(AccessRequest)
        .filter(AccessRequest.id == request_id)
        .first()
    )

    if request is None:
        return None

    # -------------------------------------------------------------
    # Zero-Payload-Decryption Key Delegation (PQC-KDP):
    # Recover only the 256-bit AES session key and re-encapsulate it
    # for the requesting doctor using ML-KEM-768.
    # The clinical medical payload remains completely untouched.
    # -------------------------------------------------------------
    record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == request.record_id)
        .first()
    )

    requesting_doctor = (
        db.query(User)
        .filter(User.id == request.doctor_id)
        .first()
    )

    if record and requesting_doctor and requesting_doctor.public_key:
        creator = (
            db.query(User)
            .filter(User.id == record.created_by)
            .first()
        )

        if creator and creator.private_key and creator.key_nonce:
            try:
                creator_priv = decrypt_private_key(creator.private_key, creator.key_nonce)
                session_key = Mediator.recover_session_key(
                    kem_ciphertext=record.kem_ciphertext,
                    encrypted_aes_key=record.encrypted_aes_key,
                    aes_key_nonce=record.aes_key_nonce,
                    private_key=creator_priv,
                    patient_id=record.patient_id,
                )

                delegated = Mediator.re_encapsulate_for_recipient(
                    session_key=session_key,
                    recipient_public_key=base64.b64decode(requesting_doctor.public_key),
                    patient_id=record.patient_id,
                )

                request.delegated_kem_ciphertext = delegated["kem_ciphertext"]
                request.delegated_encrypted_aes_key = delegated["encrypted_aes_key"]
                request.delegated_aes_key_nonce = delegated["aes_key_nonce"]
            except Exception as e:
                # Log delegation warning if key recovery fails
                print(f"[KeyDelegationWarning] Could not re-wrap key: {e}")

    request.status = "APPROVED"
    request.approved_by = admin_id
    request.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(request)

    log_action(
        db=db,
        user_id=admin_id,
        action="APPROVE_ACCESS",
        resource="MedicalRecord",
        resource_id=request.record_id,
    )

    return request



def reject_request(
    db: Session,
    request_id: int,
    admin_id: int,
):
    request = (
        db.query(AccessRequest)
        .filter(AccessRequest.id == request_id)
        .first()
    )

    if request is None:
        return None

    request.status = "REJECTED"
    request.approved_by = admin_id
    request.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(request)

    log_action(
        db=db,
        user_id=admin_id,
        action="REJECT_ACCESS",
        resource="MedicalRecord",
        resource_id=request.record_id,
    )

    return request