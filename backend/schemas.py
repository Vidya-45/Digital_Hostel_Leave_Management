"""
schemas.py
----------
Pydantic request/response models for the Anumati API.
These validate incoming JSON and shape outgoing responses.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class StudentRegisterRequest(BaseModel):
    email:    EmailStr
    password: str


class ParentRegisterRequest(BaseModel):
    email:    EmailStr
    password: str
    mobile:   str          # 10-digit mobile used to link leave applications


class WardenRegisterRequest(BaseModel):
    email:    EmailStr
    password: str


class RegisterResponse(BaseModel):
    message: str
    user_id: int

class LoginResponse(BaseModel):
    """
    Returned after a successful login.
    The frontend stores user_id in localStorage and sends it
    as the X-User-Id header on every protected request.
    """
    user_id: int          # stud_id / part_id / ward_id
    email:   str
    role:    str          # "student" | "parent" | "warden"
    mobile:  Optional[str] = None   # only set for parents


# ── Leave Application ─────────────────────────────────────────────────────────

class LeaveApplicationCreate(BaseModel):
    """Matches the student.html form fields."""
    stu_name:       str
    roll_no:        str
    room_no:        str
    stu_mobile:     str
    parent_mobile:  str
    reason:         str
    departure_date: date
    arrival_date:   date

class LeaveApplicationOut(BaseModel):
    """Returned when listing leave records."""
    leave_id:       int
    stud_id:        int
    ward_id:        Optional[int]
    stu_name:       str
    roll_no:        str
    room_no:        str
    stu_mobile:     str
    parent_mobile:  str
    reason:         str
    departure_date: date
    arrival_date:   date
    parent_status:  str
    warden_status:  str
    applied_at:     datetime

    class Config:
        from_attributes = True   # allows ORM model → Pydantic conversion


# ── Generic Responses ─────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
