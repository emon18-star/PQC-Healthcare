import base64

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
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
):
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
    db.commit()
    db.refresh(db_record)

    log_action(
        db=db,
        user_id=created_by,
        action="CREATE",
        resource="MedicalRecord",
        resource_id=db_record.id,
    )

    return db_record


def get_medical_records(db: Session):
    return db.query(MedicalRecord).all()


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
    # Load creator doctor's encrypted private key
    # ----------------------------------------

    creator = (
        db.query(User)
        .filter(User.id == record.created_by)
        .first()
    )

    if creator is None:
        raise HTTPException(
            status_code=404,
            detail="Creator doctor not found.",
        )

    if creator.private_key is None:
        raise HTTPException(
            status_code=500,
            detail="Creator doctor's private key is missing.",
        )

    if creator.key_nonce is None:
        raise HTTPException(
            status_code=500,
            detail="Creator doctor's key nonce is missing.",
        )

    # ----------------------------------------
    # Decrypt record
    # ----------------------------------------

    decrypted = Mediator.decrypt_medical_record(
        record,
        creator.private_key,
        creator.key_nonce,
    )

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