"""
routers/warden.py
-----------------
Endpoints:
  POST  /auth/warden/login              → validate plain-text password, return user_id + role
  GET   /warden/leaves                  → list parent-approved, warden-pending applications
  PATCH /warden/leaves/{leave_id}/issue → issue a gatepass (warden_status = 'Issued')

Auth: Protected routes require X-User-Id header (the ward_id returned at login).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_warden

router = APIRouter(tags=["Warden"])


# ── POST /auth/warden/login ───────────────────────────────────────────────────
@router.post("/auth/warden/login", response_model=schemas.LoginResponse)
def warden_login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a warden with email + password (plain text).
    Returns user_id and role — store these in localStorage on the frontend.
    """
    warden = db.query(models.Warden).filter(
        models.Warden.email == payload.email
    ).first()

    # Compare plain text passwords directly
    if not warden or warden.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return schemas.LoginResponse(
        user_id=warden.ward_id,
        email=warden.email,
        role="warden",
    )


# ── POST /auth/warden/register ────────────────────────────────────────────
@router.post(
    "/auth/warden/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new warden account",
)
def warden_register(payload: schemas.WardenRegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new warden account.
    Returns {message, user_id} on success.
    Returns 409 if email already exists.
    """
    existing = db.query(models.Warden).filter(
        models.Warden.email == payload.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    new_warden = models.Warden(
        email    = payload.email,
        password = payload.password,  # plain text (matches existing auth pattern)
    )
    db.add(new_warden)
    db.commit()
    db.refresh(new_warden)

    return schemas.RegisterResponse(
        message = "Warden account created successfully.",
        user_id = new_warden.ward_id,
    )


# ── GET /warden/leaves ────────────────────────────────────────────────────────
@router.get("/warden/leaves", response_model=list[schemas.LeaveApplicationOut])
def get_warden_leaves(
    db:     Session = Depends(get_db),
    warden: models.Warden = Depends(get_current_warden),
):
    """
    Return all leave applications where:
      - parent_status = 'Approved'  (parent has verified)
      - warden_status = 'Pending'   (warden hasn't acted yet)
    Requires X-User-Id header = warden's ward_id.
    """
    return (
        db.query(models.LeaveData)
        .filter(
            models.LeaveData.parent_status == models.ParentStatus.approved,
            models.LeaveData.warden_status == models.WardenStatus.pending,
        )
        .order_by(models.LeaveData.applied_at.desc())
        .all()
    )


# ── PATCH /warden/leaves/{leave_id}/issue ─────────────────────────────────────
@router.patch(
    "/warden/leaves/{leave_id}/issue",
    response_model=schemas.MessageResponse,
)
def issue_gatepass(
    leave_id: int,
    db:       Session = Depends(get_db),
    warden:   models.Warden = Depends(get_current_warden),
):
    """
    Issue a gatepass for a parent-approved leave application.
    Sets warden_status = 'Issued' and records which warden acted.
    Requires X-User-Id header = warden's ward_id.
    """
    leave = db.query(models.LeaveData).filter(
        models.LeaveData.leave_id == leave_id
    ).first()

    if not leave:
        raise HTTPException(status_code=404, detail="Leave application not found")

    if leave.parent_status != models.ParentStatus.approved:
        raise HTTPException(
            status_code=400,
            detail="Cannot issue gatepass: parent has not approved this application yet",
        )

    if leave.warden_status == models.WardenStatus.issued:
        raise HTTPException(status_code=400, detail="Gatepass already issued")

    leave.warden_status = models.WardenStatus.issued
    leave.ward_id       = warden.ward_id   # record which warden acted
    db.commit()
    return schemas.MessageResponse(message="Gatepass issued successfully")
