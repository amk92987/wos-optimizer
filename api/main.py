"""
FastAPI Backend for Bear's Den Pro Mode.
Exposes existing functionality as REST APIs for the React frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.routes import auth, heroes, profiles, dashboard

app = FastAPI(
    title="Bear's Den API",
    description="Backend API for Whiteout Survival optimizer",
    version="1.0.0"
)

# CORS for React frontend (localhost:3000 in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(heroes.router, prefix="/api/heroes", tags=["Heroes"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
def root():
    return {"message": "Bear's Den API", "version": "1.0.0"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
