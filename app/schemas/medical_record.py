from pydantic import BaseModel


class MedicalRecordBase(BaseModel):
    patient_id: int
    diagnosis: str
    symptoms: str
    treatment: str
    prescription: str | None = None
    doctor_notes: str | None = None


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    patient_id: int | None = None
    diagnosis: str | None = None
    symptoms: str | None = None
    treatment: str | None = None
    prescription: str | None = None
    doctor_notes: str | None = None


class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    created_by: int

    class Config:
        from_attributes = True