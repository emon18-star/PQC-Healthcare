from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


def create_patient(
    db: Session,
    patient: PatientCreate,
    created_by: int
):
    db_patient = Patient(
        full_name=patient.full_name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        blood_group=patient.blood_group,
        phone=patient.phone,
        email=patient.email,
        address=patient.address,
        emergency_contact=patient.emergency_contact,
        created_by=created_by,
    )

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    return db_patient


def get_patients(db: Session):
    return db.query(Patient).all()


def get_patient_by_id(
    db: Session,
    patient_id: int
):
    return (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )


def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdate
):
    patient = get_patient_by_id(db, patient_id)

    if patient is None:
        return None

    patient.full_name = patient_data.full_name
    patient.date_of_birth = patient_data.date_of_birth
    patient.gender = patient_data.gender
    patient.blood_group = patient_data.blood_group
    patient.phone = patient_data.phone
    patient.email = patient_data.email
    patient.address = patient_data.address
    patient.emergency_contact = patient_data.emergency_contact

    db.commit()
    db.refresh(patient)

    return patient


def delete_patient(
    db: Session,
    patient_id: int
):
    patient = get_patient_by_id(db, patient_id)

    if patient is None:
        return None

    db.delete(patient)
    db.commit()

    return patient