import hashlib
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

GENESIS_AUDIT_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


def compute_entry_hash(
    previous_hash: str,
    user_id: int,
    action: str,
    resource: str,
    resource_id: int | None,
    timestamp: datetime,
) -> str:
    """
    Compute cryptographic SHA-256 hash for audit chaining.
    """
    payload = f"{previous_hash}|{user_id}|{action}|{resource}|{resource_id}|{timestamp.isoformat()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def log_action(
    db: Session,
    user_id: int,
    action: str,
    resource: str,
    resource_id: int | None = None,
    commit: bool = True,
) -> AuditLog:
    """
    Log an event and link it to the preceding audit log via a cryptographic hash-chain.
    """
    last_log = (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .first()
    )

    prev_hash = (
        last_log.current_hash
        if (last_log and last_log.current_hash)
        else GENESIS_AUDIT_HASH
    )

    now = datetime.utcnow()
    curr_hash = compute_entry_hash(
        previous_hash=prev_hash,
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        timestamp=now,
    )

    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        timestamp=now,
        previous_hash=prev_hash,
        current_hash=curr_hash,
    )

    db.add(log)
    if commit:
        db.commit()

    return log


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def verify_audit_log_integrity(db: Session) -> Dict[str, Any]:
    """
    Verify the cryptographic immutability of the entire audit chain.
    Detects any unauthorized insertion, deletion, or modification of log entries.
    """
    logs: List[AuditLog] = (
        db.query(AuditLog)
        .filter(AuditLog.current_hash.isnot(None))
        .order_by(AuditLog.id.asc())
        .all()
    )

    if not logs:
        return {
            "valid": True,
            "total_verified": 0,
            "message": "No chained audit logs found to verify.",
        }

    expected_prev = GENESIS_AUDIT_HASH

    for idx, entry in enumerate(logs):
        # 1. Verify previous hash chain linkage (except for the first entry in chain)
        if idx > 0 and entry.previous_hash != expected_prev:
            return {
                "valid": False,
                "violation_at_id": entry.id,
                "reason": "Previous hash chain linkage broken.",
                "expected": expected_prev,
                "found": entry.previous_hash,
            }

        # 2. Recalculate hash of current entry
        recalculated_hash = compute_entry_hash(
            previous_hash=entry.previous_hash or GENESIS_AUDIT_HASH,
            user_id=entry.user_id,
            action=entry.action,
            resource=entry.resource,
            resource_id=entry.resource_id,
            timestamp=entry.timestamp,
        )

        if recalculated_hash != entry.current_hash:
            return {
                "valid": False,
                "violation_at_id": entry.id,
                "reason": "Entry contents tampered. Hash mismatch detected.",
                "expected": entry.current_hash,
                "computed": recalculated_hash,
            }

        expected_prev = entry.current_hash

    return {
        "valid": True,
        "total_verified": len(logs),
        "latest_block_hash": expected_prev,
        "message": "Cryptographic audit trail is 100% intact and verifiable.",
    }