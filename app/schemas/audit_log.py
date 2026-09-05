from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    resource: str
    resource_id: int | None
    timestamp: datetime

    class Config:
        from_attributes = True