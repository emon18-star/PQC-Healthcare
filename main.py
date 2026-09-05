from app.api.auth import router as auth_router
from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.patient import router as patient_router
from app.api.medical_record import router as medical_record_router
from app.api.audit_log import router as audit_log_router
from app.api.access_request import router as access_request_router

app = FastAPI(
    title="PQC Healthcare API",
    description="Post-Quantum Cryptography Framework for Secure Electronic Health Records",
    version="1.0.0",
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(medical_record_router)
app.include_router(audit_log_router)
app.include_router(access_request_router)

@app.get("/")
async def root():
    return {
        "project": "PQC Healthcare",
        "status": "Running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Backend is running successfully."
    }