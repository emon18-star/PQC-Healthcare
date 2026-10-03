from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_role
from app.database.session import get_db
from app.models.user import User

from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
)

from app.crud.medical_record import (
    create_medical_record,
    get_medical_records,
    get_medical_record_by_id,
    get_records_by_patient,
    update_medical_record,
    delete_medical_record,
    get_decrypted_record,
)

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"]
)


@router.post("/", response_model=MedicalRecordResponse)
def add_medical_record(
    medical_record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    return create_medical_record(
        db=db,
        medical_record=medical_record,
        created_by=current_user.id,
        doctor=current_user,
    )


@router.get("/", response_model=list[MedicalRecordResponse])
def read_medical_records(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor,admin"))
):
    return get_medical_records(db, skip=skip, limit=limit)


@router.get("/{record_id}", response_model=MedicalRecordResponse)
def read_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    record = get_medical_record_by_id(db, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    return record


@router.get("/patient/{patient_id}", response_model=list[MedicalRecordResponse])
def read_patient_records(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    return get_records_by_patient(db, patient_id)


@router.put("/{record_id}", response_model=MedicalRecordResponse)
def edit_medical_record(
    record_id: int,
    medical_record: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor"))
):
    record = update_medical_record(
        db,
        record_id,
        medical_record
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    return record


@router.delete("/{record_id}")
def remove_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    record = delete_medical_record(
        db,
        record_id
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    return {
        "message": "Medical record deleted successfully"
    }


@router.get("/{record_id}/decrypt")
def read_decrypted_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = get_decrypted_record(
        db=db,
        record_id=record_id,
        current_user=current_user,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )
    return record


@router.post("/{record_id}/migrate-pqc")
def migrate_record_to_pqc(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor,admin"))
):
    from app.crud.medical_record import migrate_legacy_record_to_pqc
    success = migrate_legacy_record_to_pqc(db, record_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Record cannot be migrated (already PQC-secured or invalid creator key)."
        )
    return {
        "status": "SUCCESS",
        "record_id": record_id,
        "message": f"Medical record {record_id} successfully migrated to Post-Quantum ML-KEM-768 envelope with zero downtime."
    }