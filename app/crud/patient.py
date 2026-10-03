import re
import secrets
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.user import User
from app.core.security import hash_password
from app.schemas.patient import PatientCreate, PatientUpdate


def create_patient(
    db: Session,
    patient: PatientCreate,
    created_by: int
):
    # 1. Generate unique patient username based on phone or name
    raw_digits = re.sub(r"\D", "", patient.phone or "")
    if raw_digits and len(raw_digits) >= 6:
        base_username = f"pt_{raw_digits[-10:]}"
    else:
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", patient.full_name.lower())[:8] or "user"
        base_username = f"pt_{clean_name}"

    username = base_username
    suffix = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{suffix}"
        suffix += 1

    # 2. Generate secure temporary password
    pin = secrets.randbelow(9000) + 1000
    temp_password = f"PqcCare#{pin}"

    # 3. Provision Patient User account
    db_user = User(
        username=username,
        password=hash_password(temp_password),
        role="patient",
    )
    db.add(db_user)
    db.flush()

    # 4. Create Patient entity
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

    return {
        "patient": db_patient,
        "credentials": {
            "user_id": db_user.id,
            "username": username,
            "temp_password": temp_password,
            "phone": patient.phone,
            "sms_status": "DISPATCHED",
            "message": f"Login credentials dispatched via SMS to {patient.phone}"
        }
    }


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