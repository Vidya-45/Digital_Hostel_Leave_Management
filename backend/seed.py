"""
seed.py
-------
Inserts test users into the database with PLAIN TEXT passwords.
Run ONCE after setting up the database:

    cd backend
    python seed.py

Test Credentials Created:
  Student  → email: student@test.com   | password: student123
  Parent   → email: parent@test.com    | password: parent123  | mobile: 9999988888
  Warden   → email: warden@test.com    | password: warden123

The parent's mobile (9999988888) must be entered in the student leave form as
"Parent's Mobile" for the parent to see the application on their dashboard.
"""
from database import SessionLocal
import models


def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(models.Student).count() > 0:
            print("⚠️  Database already has data. Skipping seed to avoid duplicates.")
            return

        # ── Test Student (plain text password) ────────────────────────────────
        student = models.Student(
            email    = "student@test.com",
            password = "student123",     # plain text — no hashing
        )
        db.add(student)

        # ── Test Parent (plain text password) ─────────────────────────────────
        parent = models.Parent(
            email    = "parent@test.com",
            password = "parent123",      # plain text — no hashing
            mobile   = "9999988888",     # must match parent_mobile in leave form
        )
        db.add(parent)

        # ── Test Warden (plain text password) ─────────────────────────────────
        warden = models.Warden(
            email    = "warden@test.com",
            password = "warden123",      # plain text — no hashing
        )
        db.add(warden)

        db.commit()
        print("✅ Seed complete! Test users created:")
        print("   Student → student@test.com  / student123")
        print("   Parent  → parent@test.com   / parent123  (mobile: 9999988888)")
        print("   Warden  → warden@test.com   / warden123")
        print()
        print("   💡 When submitting a leave form, use '9999988888' as Parent's Mobile")
        print("      so the test parent can see and approve the application.")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
