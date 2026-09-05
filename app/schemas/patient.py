from datetime import date

from pydantic import BaseModel, EmailStr


class PatientBase(BaseModel):
    full_name: str
    date_of_birth: date
    gender: str
    blood_group: str
    phone: str
    email: EmailStr | None = None
    address: str | None = None
    emergency_contact: str | None = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True