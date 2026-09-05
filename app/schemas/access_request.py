from datetime import datetime

from pydantic import BaseModel


class AccessRequestCreate(BaseModel):
    record_id: int
    reason: str


class AccessRequestResponse(BaseModel):
    id: int
    doctor_id: int
    record_id: int
    reason: str
    status: str
    approved_by: int | None = None
    requested_at: datetime
    approved_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }