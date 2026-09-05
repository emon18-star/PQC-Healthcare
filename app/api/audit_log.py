from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.auth import require_role
from app.models.user import User

from app.schemas.audit_log import AuditLogResponse
from app.crud.audit_log import get_logs

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "/",
    response_model=list[AuditLogResponse],
)
def read_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return get_logs(db)