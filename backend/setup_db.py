"""
setup_db.py
-----------
1. Creates the 'anumati_db' database if it doesn't exist.
2. Creates all required tables.
3. Seeds test data with PLAIN TEXT passwords.

Run this once after configuring your .env:
    python setup_db.py
"""
import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
FULL_URL = os.getenv("DATABASE_URL")

if not FULL_URL:
    print("❌ Error: DATABASE_URL not found in .env")
    exit(1)

# 1. Extract base URL (without database name) to create the DB first
# Format: mysql+pymysql://user:pass@host:port/dbname
base_url, db_name = FULL_URL.rsplit('/', 1)

try:
    print(f"--- Connecting to MySQL server at {base_url} ---")
    temp_engine = create_engine(base_url)
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        print(f"✅ Database '{db_name}' is ready.")
except Exception as e:
    print(f"❌ Failed to connect/create database: {e}")
    print("\n💡 Tip: Make sure your password in .env is correct and MySQL is running.")
    exit(1)

# 2. Connect to the actual database and create tables + seed
from database import engine, SessionLocal
from models import Base, Student, Parent, Warden

try:
    print("--- Creating tables ---")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

    print("--- Seeding test data (plain text passwords) ---")
    db = SessionLocal()

    # Check if data exists
    if db.query(Student).count() > 0:
        print("⚠️  Data already exists. Skipping seed.")
    else:
        # Passwords stored as plain text — no hashing
        db.add(Student(email="student@test.com", password="student123"))

        db.add(Parent(
            email="parent@test.com",
            password="parent123",
            mobile="9999988888"
        ))

        db.add(Warden(email="warden@test.com", password="warden123"))

        db.commit()
        print("✅ Seed complete! Test credentials:")
        print("   Student → student@test.com  / student123")
        print("   Parent  → parent@test.com   / parent123  (mobile: 9999988888)")
        print("   Warden  → warden@test.com   / warden123")
        print()
        print("   💡 Use '9999988888' as Parent's Mobile in the student leave form.")

    db.close()
    print("\n🚀 Setup successful! You can now run: uvicorn main:app --reload")

except Exception as e:
    print(f"❌ Error during setup: {e}")
