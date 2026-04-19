"""
routers/parent.py
-----------------
Endpoints:
  POST  /auth/parent/login               → validate plain-text password, return user_id + role
  GET   /parent/leaves                   → list Pending leaves linked to parent's mobile
  GET   /parent/leaves/history           → list ALL leaves (Pending + Approved) linked to parent's mobile
  PATCH /parent/leaves/{leave_id}/approve → approve a leave application

Auth: Protected routes require X-User-Id header (the part_id returned at login).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_parent

router = APIRouter(tags=["Parent"])


# ── POST /auth/parent/login ───────────────────────────────────────────────────
@router.post("/auth/parent/login", response_model=schemas.LoginResponse)
def parent_login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a parent with email + password (plain text).
    Returns user_id, role, and mobile — store these in localStorage on the frontend.
    """
    parent = db.query(models.Parent).filter(
        models.Parent.email == payload.email
    ).first()

    # Compare plain text passwords directly
    if not parent or parent.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return schemas.LoginResponse(
        user_id=parent.part_id,
        email=parent.email,
        role="parent",
        mobile=parent.mobile,
    )


# ── POST /auth/parent/register ────────────────────────────────────────────
@router.post(
    "/auth/parent/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new parent account",
)
def parent_register(payload: schemas.ParentRegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new parent account.
    The mobile must be unique and will be used to link leave applications.
    Returns {message, user_id} on success.
    Returns 409 if email or mobile already exists.
    """
    if db.query(models.Parent).filter(models.Parent.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    if db.query(models.Parent).filter(models.Parent.mobile == payload.mobile).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This mobile number is already registered to another account.",
        )

    new_parent = models.Parent(
        email    = payload.email,
        password = payload.password,  # plain text (matches existing auth pattern)
        mobile   = payload.mobile,
    )
    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)

    return schemas.RegisterResponse(
        message = "Parent account created successfully.",
        user_id = new_parent.part_id,
    )


# ── GET /parent/leaves ────────────────────────────────────────────────────────
@router.get("/parent/leaves", response_model=list[schemas.LeaveApplicationOut])
def get_parent_leaves(
    db:     Session = Depends(get_db),
    parent: models.Parent = Depends(get_current_parent),
):
    """
    Return all Pending leave applications where parent_mobile matches
    the logged-in parent's registered mobile number.
    Requires X-User-Id header = parent's part_id.
    """
    return (
        db.query(models.LeaveData)
        .filter(
            models.LeaveData.parent_mobile == parent.mobile,
            models.LeaveData.parent_status == models.ParentStatus.pending,
        )
        .order_by(models.LeaveData.applied_at.desc())
        .all()
    )


# ── GET /parent/leaves/history ────────────────────────────────────────────────
@router.get("/parent/leaves/history", response_model=list[schemas.LeaveApplicationOut])
def get_parent_leaves_history(
    db:     Session = Depends(get_db),
    parent: models.Parent = Depends(get_current_parent),
):
    """
    Return ALL leave applications (Pending + Approved) where parent_mobile
    matches the logged-in parent's registered mobile number.
    Used to populate the history table on the parent dashboard.
    Requires X-User-Id header = parent's part_id.
    """
    return (
        db.query(models.LeaveData)
        .filter(
            models.LeaveData.parent_mobile == parent.mobile,
        )
        .order_by(models.LeaveData.applied_at.desc())
        .all()
    )


# ── PATCH /parent/leaves/{leave_id}/approve ───────────────────────────────────
@router.patch(
    "/parent/leaves/{leave_id}/approve",
    response_model=schemas.MessageResponse,
)
def approve_leave(
    leave_id: int,
    db:       Session = Depends(get_db),
    parent:   models.Parent = Depends(get_current_parent),
):
    """
    Approve a specific leave application.
    Verifies that this leave's parent_mobile matches the authenticated parent.
    Requires X-User-Id header = parent's part_id.
    """
    leave = db.query(models.LeaveData).filter(
        models.LeaveData.leave_id == leave_id
    ).first()

    if not leave:
        raise HTTPException(status_code=404, detail="Leave application not found")

    if leave.parent_mobile != parent.mobile:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to approve this application",
        )

    if leave.parent_status == models.ParentStatus.approved:
        raise HTTPException(status_code=400, detail="Already approved")

    leave.parent_status = models.ParentStatus.approved
    db.commit()
    return schemas.MessageResponse(message="Leave approved by parent successfully")
