from fastapi import FastAPI
from app.api.user import router as user_router

app = FastAPI(
    title="PQC Healthcare API",
    description="Post-Quantum Cryptography Framework for Secure Electronic Health Records",
    version="1.0.0",
)

app.include_router(user_router)


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