"""
main.py
-------
FastAPI application entry point for the Anumati Hostel Leave Management system.

Run with:
    cd backend
    uvicorn main:app --reload

Swagger UI available at: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import student, parent, warden

# ── Create all tables if they don't exist ─────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App init ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Anumati — Digital Hostel Leave Management API",
    description=(
        "Backend API for managing hostel leave applications.\n\n"
        "**Flow:** Student submits → Parent approves → Warden issues gatepass.\n\n"
        "Use the `/auth/{role}/login` endpoints first to get a Bearer token, "
        "then click **Authorize** and paste it in to access protected routes."
    ),
    version="1.0.0",
    contact={
        "name": "Anumati Dev",
    },
)

# ── CORS (allow all origins for local development) ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # restrict this to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include routers ───────────────────────────────────────────────────────────
app.include_router(student.router)
app.include_router(parent.router)
app.include_router(warden.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "Anumati API is running. Visit /docs for Swagger UI.",
    }
