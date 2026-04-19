"""
auth.py
-------
Simplified authentication — no JWT, no bcrypt.
Passwords are stored as plain text in the database.

Protected routes use a simple X-User-Id header:
  - Frontend sends the user's numeric ID after login
  - Backend looks up the ID in the correct table to verify
"""
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models


# ── Dependency: get current student ──────────────────────────────────────────
def get_current_student(
    x_user_id: int = Header(..., description="Student's stud_id from login response"),
    db: Session = Depends(get_db),
) -> models.Student:
    student = db.query(models.Student).filter(
        models.Student.stud_id == x_user_id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: student not found",
        )
    return student


# ── Dependency: get current parent ────────────────────────────────────────────
def get_current_parent(
    x_user_id: int = Header(..., description="Parent's part_id from login response"),
    db: Session = Depends(get_db),
) -> models.Parent:
    parent = db.query(models.Parent).filter(
        models.Parent.part_id == x_user_id
    ).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: parent not found",
        )
    return parent


# ── Dependency: get current warden ────────────────────────────────────────────
def get_current_warden(
    x_user_id: int = Header(..., description="Warden's ward_id from login response"),
    db: Session = Depends(get_db),
) -> models.Warden:
    warden = db.query(models.Warden).filter(
        models.Warden.ward_id == x_user_id
    ).first()
    if not warden:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: warden not found",
        )
    return warden
