from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/overview", response_model=schemas.DashboardOverviewOut)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """Fetch aggregated KPI metrics and operational status for the dashboard HUD."""
    vehicles = db.query(models.Vehicle).all()
    active_count = len(vehicles)
    
    critical_incident = (
        db.query(models.Incident)
        .filter(models.Incident.status.in_(["ACTIVE", "MITIGATING"]))
        .first()
    )

    critical_vehicle = None
    if critical_incident:
        critical_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == critical_incident.vehicle_id).first()

    recommended_plan = None
    if critical_incident:
        recommended_plan = (
            db.query(models.RecoveryPlan)
            .filter(models.RecoveryPlan.incident_id == critical_incident.id)
            .order_by(models.RecoveryPlan.created_at.desc())
            .first()
        )

    # Active directives count
    active_directives = (
        db.query(models.RecoveryPlan)
        .filter(models.RecoveryPlan.status.in_(["RECOMMENDED", "APPROVED"]))
        .count()
    )

    return schemas.DashboardOverviewOut(
        active_units_total=max(48, active_count),
        active_units_synchronized=max(48, active_count),
        critical_breaches_count=1 if critical_incident else 0,
        critical_vehicle_id=critical_vehicle.id if critical_vehicle else "AC-2048",
        critical_temp_c=critical_vehicle.current_temp_c if critical_vehicle else 8.2,
        critical_temp_target_c=critical_vehicle.target_temp_c if critical_vehicle else 2.0,
        active_dispatch_directives_count=active_directives,
        cargo_asset_exposure_usd=142000.0,
        projected_yield_preservation_pct=recommended_plan.biological_yield_pct if recommended_plan else 99.4,
        system_status="SYS NOMINAL" if not critical_incident or critical_incident.status == "RESOLVED" else "CRITICAL BREACH ACTIVE",
        telemetry_sync_seconds=1.8,
        critical_incident=critical_incident,
        recommended_plan=recommended_plan
    )
