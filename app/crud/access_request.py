from datetime import datetime

from sqlalchemy.orm import Session

from app.models.access_request import AccessRequest
from app.models.medical_record import MedicalRecord
from app.crud.audit_log import log_action


def create_access_request(
    db: Session,
    doctor_id: int,
    record_id: int,
    reason: str,
):
    # Verify the record exists
    record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )

    if record is None:
        return None

    # Prevent duplicate pending requests
    existing = (
        db.query(AccessRequest)
        .filter(
            AccessRequest.doctor_id == doctor_id,
            AccessRequest.record_id == record_id,
            AccessRequest.status == "PENDING",
        )
        .first()
    )

    if existing:
        return existing

    request = AccessRequest(
        doctor_id=doctor_id,
        record_id=record_id,
        reason=reason,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    log_action(
        db=db,
        user_id=doctor_id,
        action="REQUEST_ACCESS",
        resource="MedicalRecord",
        resource_id=record_id,
    )

    return request


def get_pending_requests(db: Session):
    return (
        db.query(AccessRequest)
        .filter(AccessRequest.status == "PENDING")
        .order_by(AccessRequest.requested_at.desc())
        .all()
    )


def approve_request(
    db: Session,
    request_id: int,
    admin_id: int,
):
    request = (
        db.query(AccessRequest)
        .filter(AccessRequest.id == request_id)
        .first()
    )

    if request is None:
        return None

    request.status = "APPROVED"
    request.approved_by = admin_id
    request.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(request)

    log_action(
        db=db,
        user_id=admin_id,
        action="APPROVE_ACCESS",
        resource="MedicalRecord",
        resource_id=request.record_id,
    )

    return request


def reject_request(
    db: Session,
    request_id: int,
    admin_id: int,
):
    request = (
        db.query(AccessRequest)
        .filter(AccessRequest.id == request_id)
        .first()
    )

    if request is None:
        return None

    request.status = "REJECTED"
    request.approved_by = admin_id
    request.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(request)

    log_action(
        db=db,
        user_id=admin_id,
        action="REJECT_ACCESS",
        resource="MedicalRecord",
        resource_id=request.record_id,
    )

    return request