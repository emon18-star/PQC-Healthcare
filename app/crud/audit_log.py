from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: int,
    action: str,
    resource: str,
    resource_id: int | None = None,
):
    print("AUDIT LOG CALLED")

    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
    )

    db.add(log)
    db.commit()

    print("AUDIT LOG SAVED")

    return log


def get_logs(db: Session):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )