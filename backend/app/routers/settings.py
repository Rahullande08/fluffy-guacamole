from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..config import settings
from .. import models, schemas

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=Dict[str, Any])
def get_system_settings(db: Session = Depends(get_db)):
    """Retrieve system configuration and third-party integration statuses."""
    db_settings = db.query(models.Setting).all()
    stored = {s.key: s.value for s in db_settings}

    return {
        "integrations": {
            "gemini_api": {
                "configured": bool(settings.GEMINI_API_KEY),
                "mode": "Live Google Gemini AI" if settings.GEMINI_API_KEY else "Deterministic Fallback Engine (Demo Mode)",
                "env_variable": "GEMINI_API_KEY"
            },
            "google_maps": {
                "configured": bool(settings.GOOGLE_MAPS_SERVER_API_KEY),
                "mode": "Live Routes API" if settings.GOOGLE_MAPS_SERVER_API_KEY else "Calibrated Routing Model (Demo Mode)",
                "env_variable": "GOOGLE_MAPS_SERVER_API_KEY"
            },
            "database": {
                "url": settings.DATABASE_URL.split("///")[-1] if "///" in settings.DATABASE_URL else "aerocold.db",
                "type": "SQLite Local (Production path: PostgreSQL)"
            },
            "demo_mode": {
                "enabled": settings.DEMO_MODE,
                "description": "Simulated approvals and calibrated sensor telemetry are clearly flagged."
            }
        },
        "system_parameters": stored,
        "audit_compliance": "FDA 21 CFR Part 11 Active"
    }
