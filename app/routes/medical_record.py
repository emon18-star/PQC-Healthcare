from fastapi import APIRouter

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"],
)