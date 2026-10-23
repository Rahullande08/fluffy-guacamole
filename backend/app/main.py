import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, Base, SessionLocal, get_db
from .seed_data import seed_database
from .routers import (
    dashboard,
    fleet,
    incidents,
    recovery,
    analytics,
    notifications,
    settings as settings_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    # Seed default demonstration data
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="4.8.2-PROD",
    description="Autonomous Cold-Chain Telematics & Thermal Risk Recovery Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "system": "AeroCold Autonomous Engine",
        "version": "v4.8.2-PROD",
        "telemetry_stream": "NOMINAL",
        "demo_mode": settings.DEMO_MODE
    }

# Register API v1 Routers
api_v1 = FastAPI()
api_v1.include_router(dashboard.router)
api_v1.include_router(fleet.router)
api_v1.include_router(incidents.router)
api_v1.include_router(recovery.router)
api_v1.include_router(analytics.router)
api_v1.include_router(notifications.router)
api_v1.include_router(settings_router.router)

app.mount(settings.API_V1_PREFIX, api_v1)

# Frontend Static Files & SPA Routing
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_root():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "AeroCold Intelligence API is running."}

    @app.get("/overview")
    @app.get("/operations-overview")
    def serve_overview():
        return FileResponse(os.path.join(FRONTEND_DIR, "overview.html"))

    @app.get("/incident")
    @app.get("/incidents")
    def serve_incident():
        return FileResponse(os.path.join(FRONTEND_DIR, "incident.html"))

    @app.get("/recovery-planner")
    @app.get("/recovery")
    def serve_recovery():
        return FileResponse(os.path.join(FRONTEND_DIR, "recovery.html"))

    @app.get("/fleet")
    @app.get("/live-fleet")
    def serve_fleet():
        return FileResponse(os.path.join(FRONTEND_DIR, "fleet.html"))

    @app.get("/analytics")
    def serve_analytics():
        return FileResponse(os.path.join(FRONTEND_DIR, "analytics.html"))

    @app.get("/settings")
    def serve_settings():
        return FileResponse(os.path.join(FRONTEND_DIR, "settings.html"))
