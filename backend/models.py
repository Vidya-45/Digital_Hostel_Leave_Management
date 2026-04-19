"""
models.py
---------
SQLAlchemy ORM models for the Anumati leave management system.

Tables:
  - students   → stores student credentials
  - parents    → stores parent credentials + mobile (used for linking)
  - wardens    → stores warden credentials
  - leave_data → central leave application table (FK → students, wardens)
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Date,
    DateTime, Enum, ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base
import enum


# ── Enum Types ────────────────────────────────────────────────────────────────

class ParentStatus(str, enum.Enum):
    pending  = "Pending"
    approved = "Approved"

class WardenStatus(str, enum.Enum):
    pending = "Pending"
    issued  = "Issued"


# ── ORM Models ────────────────────────────────────────────────────────────────

class Student(Base):
    __tablename__ = "students"

    stud_id    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)              # bcrypt hash
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship (optional — useful for queries)
    leaves = relationship("LeaveData", back_populates="student")


class Parent(Base):
    __tablename__ = "parents"

    part_id    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)              # bcrypt hash
    mobile     = Column(String(15),  unique=True, nullable=False) # links to leave_data.parent_mobile
    created_at = Column(DateTime, default=datetime.utcnow)


class Warden(Base):
    __tablename__ = "wardens"

    ward_id    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email      = Column(String(255), unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)              # bcrypt hash
    created_at = Column(DateTime, default=datetime.utcnow)

    leaves = relationship("LeaveData", back_populates="warden")


class LeaveData(Base):
    __tablename__ = "leave_data"

    leave_id       = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # FK references
    stud_id        = Column(Integer, ForeignKey("students.stud_id"), nullable=False)
    ward_id        = Column(Integer, ForeignKey("wardens.ward_id"),  nullable=True)  # set when warden acts

    # Form fields (from student.html)
    stu_name       = Column(String(255), nullable=False)
    roll_no        = Column(String(50),  nullable=False)
    room_no        = Column(String(50),  nullable=False)
    stu_mobile     = Column(String(15),  nullable=False)
    parent_mobile  = Column(String(15),  nullable=False)    # key used to link parent
    reason         = Column(Text,        nullable=False)
    departure_date = Column(Date,        nullable=False)
    arrival_date   = Column(Date,        nullable=False)

    # Status tracking
    parent_status  = Column(Enum(ParentStatus), default=ParentStatus.pending)
    warden_status  = Column(Enum(WardenStatus), default=WardenStatus.pending)

    applied_at     = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="leaves")
    warden  = relationship("Warden",  back_populates="leaves")
