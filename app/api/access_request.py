from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User

from app.schemas.access_request import (
    AccessRequestCreate,
    AccessRequestResponse,
)

from app.crud.access_request import (
    create_access_request,
    get_pending_requests,
    get_all_requests,
    approve_request,
    reject_request,
)

router = APIRouter(
    prefix="/access-requests",
    tags=["Access Requests"],
)


@router.get("/", response_model=list[AccessRequestResponse])
def all_requests(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin,doctor")),
):
    return get_all_requests(db, skip=skip, limit=limit)


@router.post("/", response_model=AccessRequestResponse)
def request_access(
    request: AccessRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    result = create_access_request(
        db=db,
        doctor_id=current_user.id,
        record_id=request.record_id,
        reason=request.reason,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found",
        )

    return result


@router.get("/pending", response_model=list[AccessRequestResponse])
def pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return get_pending_requests(db)


@router.put("/{request_id}/approve", response_model=AccessRequestResponse)
def approve(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    result = approve_request(
        db=db,
        request_id=request_id,
        admin_id=current_user.id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Access request not found",
        )

    return result


@router.put("/{request_id}/reject", response_model=AccessRequestResponse)
def reject(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    result = reject_request(
        db=db,
        request_id=request_id,
        admin_id=current_user.id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Access request not found",
        )

    return result