# API Application entrypoint - Mumbai Pooler & High-Performance Optimizations Active
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.patient import router as patient_router
from app.api.medical_record import router as medical_record_router
from app.api.audit_log import router as audit_log_router
from app.api.access_request import router as access_request_router
from app.api.stats import router as stats_router

app = FastAPI(
    title="Model Hospital - PQC Healthcare API",
    description="Post-Quantum Cryptography (ML-KEM-768 & AES-256-GCM) Framework for Secure Electronic Health Records",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(medical_record_router)
app.include_router(audit_log_router)
app.include_router(access_request_router)
app.include_router(stats_router)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root directly to Swagger UI Documentation."""
    return RedirectResponse(url="/docs")

@app.get("/api/info")
async def info():
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