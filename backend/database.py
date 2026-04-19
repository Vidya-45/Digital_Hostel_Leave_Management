"""
database.py
-----------
Creates the SQLAlchemy Engine and SessionLocal from the DATABASE_URL
stored in .env. Import `get_db` as a FastAPI dependency in your routes.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Please fill in backend/.env before starting the server."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # auto-reconnect on stale connections
    pool_recycle=3600,       # recycle connections every hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
