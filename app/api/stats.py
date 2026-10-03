from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/stats",
    tags=["Dashboard Stats"]
)

@router.get("/overview")
def get_overview_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_patients = db.execute(text('SELECT COUNT(*) FROM patients')).scalar() or 0
    total_records = db.execute(text('SELECT COUNT(*) FROM medical_records')).scalar() or 0
    total_logs = db.execute(text('SELECT COUNT(*) FROM audit_logs')).scalar() or 0
    total_users = db.execute(text('SELECT COUNT(*) FROM users')).scalar() or 0
    pending_requests = db.execute(text("SELECT COUNT(*) FROM access_requests WHERE status = 'PENDING'")).scalar() or 0
    
    return {
        "patients": total_patients,
        "medical_records": total_records,
        "audit_logs": total_logs,
        "users": total_users,
        "pending_requests": pending_requests,
        "pqc_engine": {
            "algorithm": "ML-KEM-768 (NIST FIPS 203)",
            "hybrid_cipher": "AES-256-GCM Authenticated",
            "security_category": "NIST Security Level 3 (Quantum Resistant)",
            "status": "ACTIVE_PROTECTED"
        },
        "database": {
            "engine": "PostgreSQL / Supabase Pooler",
            "status": "CONNECTED"
        }
    }
