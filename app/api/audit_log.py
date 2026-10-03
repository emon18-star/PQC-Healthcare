from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.auth import require_role
from app.models.user import User

from app.schemas.audit_log import AuditLogResponse
from app.crud.audit_log import get_logs, verify_audit_log_integrity

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "/verify",
    summary="Cryptographically verify audit chain integrity",
)
def verify_audit_chain(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin,doctor")),
):
    """
    Validates that no audit logs have been tampered, modified, or deleted.
    """
    return verify_audit_log_integrity(db)


@router.get(
    "/",
    response_model=list[AuditLogResponse],
)
def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin,doctor")),
):
    return get_logs(db, skip=skip, limit=limit)