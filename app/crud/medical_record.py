import base64

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.access_request import AccessRequest

from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
)

from app.core.mediator import Mediator
from app.crud.audit_log import log_action


def create_medical_record(
    db: Session,
    medical_record: MedicalRecordCreate,
    created_by: int,
    doctor: User | None = None,
):
    if doctor is None:
        doctor = (
            db.query(User)
            .filter(User.id == created_by)
            .first()
        )

    if doctor is None:
        raise ValueError("Doctor not found.")

    if doctor.public_key is None:
        raise ValueError("Doctor has no public key.")

    encrypted = Mediator.encrypt_medical_record(
        medical_record,
        base64.b64decode(doctor.public_key),
    )

    db_record = MedicalRecord(
        patient_id=medical_record.patient_id,
        encrypted_record=encrypted["encrypted_record"],
        kem_ciphertext=encrypted["kem_ciphertext"],
        encrypted_aes_key=encrypted["encrypted_aes_key"],
        aes_key_nonce=encrypted["aes_key_nonce"],
        created_by=created_by,
    )

    db.add(db_record)
    db.flush()

    log_action(
        db=db,
        user_id=created_by,
        action="CREATE",
        resource="MedicalRecord",
        resource_id=db_record.id,
        commit=False,
    )

    db.commit()

    return db_record


def get_medical_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MedicalRecord).order_by(MedicalRecord.id.desc()).offset(skip).limit(limit).all()


def get_medical_record_by_id(
    db: Session,
    record_id: int,
):
    return (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )


def get_records_by_patient(
    db: Session,
    patient_id: int,
):
    return (
        db.query(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient_id)
        .all()
    )


def update_medical_record(
    db: Session,
    record_id: int,
    record_data: MedicalRecordUpdate,
):
    """
    Placeholder.
    Updating encrypted medical records
    will be implemented later.
    """
    return get_medical_record_by_id(db, record_id)


def delete_medical_record(
    db: Session,
    record_id: int,
):
    record = get_medical_record_by_id(
        db,
        record_id,
    )

    if record is None:
        return None

    db.delete(record)
    db.commit()

    return record


def get_decrypted_record(
    db: Session,
    record_id: int,
    current_user: User,
):
    record = get_medical_record_by_id(
        db,
        record_id,
    )

    if record is None:
        return None

    # ----------------------------------------
    # Authorization
    # ----------------------------------------

    if current_user.role.lower() == "doctor":

        # If this doctor is NOT the creator,
        # approval from admin is required.
        if record.created_by != current_user.id:

            approved_request = (
                db.query(AccessRequest)
                .filter(
                    AccessRequest.record_id == record.id,
                    AccessRequest.doctor_id == current_user.id,
                    AccessRequest.status == "APPROVED",
                )
                .first()
            )

            if approved_request is None:

                log_action(
                    db=db,
                    user_id=current_user.id,
                    action="ACCESS_DENIED",
                    resource="MedicalRecord",
                    resource_id=record.id,
                )

                raise HTTPException(
                    status_code=403,
                    detail="Access request has not been approved.",
                )

    # ----------------------------------------
    # Dual-Stack Migration Support:
    # Check if record is Post-Quantum or Legacy
    # ----------------------------------------
    if getattr(record, "kem_ciphertext", None) is None:
        # Legacy fallback mode: Gracefully handle pre-PQC records without system disruption
        import json
        try:
            decrypted = json.loads(record.encrypted_record) if isinstance(record.encrypted_record, str) else record.encrypted_record
        except Exception:
            decrypted = {"raw_legacy_record": str(record.encrypted_record)}
        
        decrypted = Mediator.filter_record_for_role(decrypted, current_user.role)
        decrypted["id"] = record.id
        decrypted["patient_id"] = record.patient_id
        decrypted["created_by"] = record.created_by
        decrypted["is_pqc_secured"] = False
        decrypted["migration_status"] = "PENDING_PQC_MIGRATION"

        log_action(
            db=db,
            user_id=current_user.id,
            action="DECRYPT_LEGACY",
            resource="MedicalRecord",
            resource_id=record.id,
        )
        return decrypted

    # ----------------------------------------
    # Decrypt record using Zero-Trust Principles
    # ----------------------------------------

    # Case 1: Delegated Doctor with approved re-wrapped PQC session key
    if (
        current_user.id != record.created_by
        and approved_request is not None
        and approved_request.delegated_kem_ciphertext is not None
    ):
        decrypted = Mediator.decrypt_medical_record(
            record=record,
            encrypted_private_key=current_user.private_key,
            key_nonce=current_user.key_nonce,
            user_role=current_user.role,
            kem_ciphertext_override=approved_request.delegated_kem_ciphertext,
            encrypted_aes_key_override=approved_request.delegated_encrypted_aes_key,
            aes_key_nonce_override=approved_request.delegated_aes_key_nonce,
        )

    # Case 2: Creator Doctor accessing their own patient record
    elif current_user.id == record.created_by:
        decrypted = Mediator.decrypt_medical_record(
            record=record,
            encrypted_private_key=current_user.private_key,
            key_nonce=current_user.key_nonce,
            user_role=current_user.role,
        )

    # Case 3: Admin or legacy fallback accessing via creator's encrypted key
    else:
        creator = (
            db.query(User)
            .filter(User.id == record.created_by)
            .first()
        )

        if creator is None or creator.private_key is None or creator.key_nonce is None:
            raise HTTPException(
                status_code=500,
                detail="Record decryption keys could not be resolved.",
            )

        decrypted = Mediator.decrypt_medical_record(
            record=record,
            encrypted_private_key=creator.private_key,
            key_nonce=creator.key_nonce,
            user_role=current_user.role,
        )

    decrypted["is_pqc_secured"] = True
    decrypted["migration_status"] = "PQC_SECURED"

    # ----------------------------------------
    # Audit Log
    # ----------------------------------------

    log_action(
        db=db,
        user_id=current_user.id,
        action="DECRYPT",
        resource="MedicalRecord",
        resource_id=record.id,
    )

    return decrypted


def migrate_legacy_record_to_pqc(db: Session, record_id: int) -> bool:
    """
    Zero-Downtime Lazy Migration Worker:
    Converts a legacy unencrypted or classical record into the ML-KEM-768 envelope
    in the background during off-peak hours without locking live clinical operations.
    """
    import json
    record = get_medical_record_by_id(db, record_id)
    if not record or getattr(record, "kem_ciphertext", None) is not None:
        return False  # Already PQC or doesn't exist
    
    creator = db.query(User).filter(User.id == record.created_by).first()
    if not creator or not creator.public_key:
        return False
    
    try:
        data = json.loads(record.encrypted_record) if isinstance(record.encrypted_record, str) else record.encrypted_record
    except Exception:
        data = {"diagnosis": str(record.encrypted_record)}
        
    class RecordProxy:
        patient_id = record.patient_id
        diagnosis = data.get("diagnosis", "Legacy record")
        symptoms = data.get("symptoms", "")
        treatment = data.get("treatment", "")
        prescription = data.get("prescription", "")
        doctor_notes = data.get("doctor_notes", "")
        
    encrypted = Mediator.encrypt_medical_record(RecordProxy(), base64.b64decode(creator.public_key))
    record.encrypted_record = encrypted["encrypted_record"]
    record.kem_ciphertext = encrypted["kem_ciphertext"]
    record.encrypted_aes_key = encrypted["encrypted_aes_key"]
    record.aes_key_nonce = encrypted["aes_key_nonce"]
    db.commit()

    log_action(
        db=db,
        user_id=creator.id,
        action="MIGRATE_TO_PQC",
        resource="MedicalRecord",
        resource_id=record.id,
    )
    return True