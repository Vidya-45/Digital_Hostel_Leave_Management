"""
routers/student.py
------------------
Endpoints:
  POST /auth/student/login    → validate plain-text password, return user_id + role
  POST /student/leave         → submit a new leave application
  GET  /student/leaves        → get all leaves for the logged-in student

Auth: Protected routes require X-User-Id header (the stud_id returned at login).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_student

router = APIRouter(tags=["Student"])


# ── POST /auth/student/login ──────────────────────────────────────────────────
@router.post("/auth/student/login", response_model=schemas.LoginResponse)
def student_login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a student with email + password (plain text).
    Returns user_id and role — store these in localStorage on the frontend.
    """
    student = db.query(models.Student).filter(
        models.Student.email == payload.email
    ).first()

    # Compare plain text passwords directly
    if not student or student.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return schemas.LoginResponse(
        user_id=student.stud_id,
        email=student.email,
        role="student",
    )


# ── POST /auth/student/register ────────────────────────────────────────────
@router.post(
    "/auth/student/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
def student_register(payload: schemas.StudentRegisterRequest, db: Session = Depends(get_db)):
    """
    Create a new student account.
    Returns {message, user_id} on success.
    Returns 409 if email already exists.
    """
    existing = db.query(models.Student).filter(
        models.Student.email == payload.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    new_student = models.Student(
        email    = payload.email,
        password = payload.password,  # plain text (matches existing auth pattern)
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return schemas.RegisterResponse(
        message = "Student account created successfully.",
        user_id = new_student.stud_id,
    )


# ── POST /student/leave ───────────────────────────────────────────────────────
@router.post(
    "/student/leave",
    response_model=schemas.LeaveApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_leave(
    payload: schemas.LeaveApplicationCreate,
    db:      Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """
    Submit a new leave application.
    Requires X-User-Id header = student's stud_id.
    """
    new_leave = models.LeaveData(
        stud_id        = student.stud_id,
        stu_name       = payload.stu_name,
        roll_no        = payload.roll_no,
        room_no        = payload.room_no,
        stu_mobile     = payload.stu_mobile,
        parent_mobile  = payload.parent_mobile,
        reason         = payload.reason,
        departure_date = payload.departure_date,
        arrival_date   = payload.arrival_date,
    )
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave


# ── GET /student/leaves ───────────────────────────────────────────────────────
@router.get("/student/leaves", response_model=list[schemas.LeaveApplicationOut])
def get_my_leaves(
    db:      Session = Depends(get_db),
    student: models.Student = Depends(get_current_student),
):
    """
    Return all leave applications submitted by the logged-in student.
    Requires X-User-Id header = student's stud_id.
    """
    return (
        db.query(models.LeaveData)
        .filter(models.LeaveData.stud_id == student.stud_id)
        .order_by(models.LeaveData.applied_at.desc())
        .all()
    )
