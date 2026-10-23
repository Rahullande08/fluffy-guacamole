from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..services.gemini_agent import run_incident_recovery_agent
from ..services.agent_tools import (
    get_vehicle_telemetry,
    get_cargo_handling_rules,
    calculate_temperature_risk,
    find_recovery_facilities,
    compare_recovery_options,
    create_recovery_plan
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[schemas.IncidentOut])
def list_incidents(
    status: Optional[str] = Query(None, description="ACTIVE, MITIGATING, RESOLVED"),
    severity: Optional[str] = Query(None, description="CRITICAL, WARNING"),
    db: Session = Depends(get_db)
):
    """List all cold-chain incidents."""
    query = db.query(models.Incident)
    if status:
        query = query.filter(models.Incident.status == status)
    if severity:
        query = query.filter(models.Incident.severity == severity)
    return query.order_by(models.Incident.created_at.desc()).all()

@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve full incident details including vehicle telematics and generated recovery plans."""
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident

@router.post("/{incident_id}/analyze", response_model=schemas.IncidentAnalyzeResponse)
def analyze_incident(
    incident_id: str,
    payload: Optional[schemas.IncidentAnalyzeRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Run the AI Recovery Agent on an incident.
    Reads vehicle telemetry, applies cargo rules, evaluates decay rate, searches candidate facilities,
    and returns structured reasoning with a persisted recovery plan.
    """
    try:
        result = run_incident_recovery_agent(db, incident_id)
        return schemas.IncidentAnalyzeResponse(
            incident_id=result["incident_id"],
            risk_level=result["risk_level"],
            temperature_breach_c=result["temperature_breach_c"],
            drift_rate_c_per_min=result["drift_rate_c_per_min"],
            time_to_quality_loss_minutes=result["time_to_quality_loss_minutes"],
            salvage_percentage_projected=result["salvage_percentage_projected"],
            ai_analysis_narrative=result["ai_analysis_narrative"],
            evidence_checklist=result["evidence_checklist"],
            suggested_recovery_facility=result["suggested_recovery_facility"],
            confidence_score=result["confidence_score"],
            recovery_plan=result["recovery_plan"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {str(e)}")

@router.get("/{incident_id}/recovery-plans", response_model=List[schemas.RecoveryPlanOut])
def get_incident_recovery_plans(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve all recovery plans generated for this incident."""
    plans = (
        db.query(models.RecoveryPlan)
        .filter(models.RecoveryPlan.incident_id == incident_id)
        .order_by(models.RecoveryPlan.created_at.desc())
        .all()
    )
    return plans

@router.post("/{incident_id}/recovery-plans", response_model=schemas.RecoveryPlanOut)
def create_custom_recovery_plan(
    incident_id: str,
    payload: schemas.RecoveryPlanCreate,
    db: Session = Depends(get_db)
):
    """Create or manually select a candidate recovery facility for an incident."""
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    facility = db.query(models.RecoveryFacility).filter(models.RecoveryFacility.id == payload.facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility {payload.facility_id} not found")

    plan = create_recovery_plan(
        db=db,
        incident_id=incident_id,
        vehicle_id=incident.vehicle_id,
        facility_id=facility.id,
        confidence_score=0.96 if facility.is_recommended else 0.88,
        estimated_arrival_minutes=facility.estimated_travel_minutes,
        projected_salvage_usd=141148.0 if facility.is_recommended else 135000.0,
        biological_yield_pct=99.4 if facility.is_recommended else 94.2,
        ai_reasoning=payload.reason or f"Dispatcher selected {facility.short_name} as primary cross-dock target.",
        evidence_summary="Manual dispatcher selection with bay intake clearance verified.",
        assumptions="Standard highway transit speeds along diversion vector."
    )
    return plan

@router.post("/{incident_id}/simulate-spike")
def simulate_thermal_spike(incident_id: str, db: Session = Depends(get_db)):
    """Interactive demo trigger: Simulates a sudden +2.4°C thermal spike in telemetry."""
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == incident.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Add spike
    vehicle.current_temp_c = round(vehicle.current_temp_c + 2.4, 1)
    incident.excursion_temp_c = vehicle.current_temp_c
    incident.drift_rate_c_per_min = 0.35
    incident.time_to_spoilage_minutes = 64

    # Add sensor reading
    new_reading = models.SensorReading(
        vehicle_id=vehicle.id,
        sensor_code="T-04",
        temperature_c=vehicle.current_temp_c,
        humidity_pct=92.0,
        timestamp=datetime.now(timezone.utc),
        is_anomaly=True,
        is_simulated=True
    )
    db.add(new_reading)

    # Activity log
    log = models.ActivityLog(
        event_type="SIMULATED_THERMAL_SPIKE",
        message=f"Simulated thermal spike triggered on Unit {vehicle.id}: +2.4°C surge to {vehicle.current_temp_c}°C.",
        vehicle_id=vehicle.id,
        incident_id=incident.id,
        user_name="Interactive Demo Operator"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "message": f"Spike simulated. Unit {vehicle.id} temperature is now {vehicle.current_temp_c}°C",
        "new_temp_c": vehicle.current_temp_c,
        "drift_rate": incident.drift_rate_c_per_min
    }

@router.post("/{incident_id}/reset-demo")
def reset_incident_demo(incident_id: str, db: Session = Depends(get_db)):
    """Reset incident and vehicle state for replay demonstration."""
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == incident.vehicle_id).first()
    if vehicle:
        vehicle.status = "ALERT"
        vehicle.current_temp_c = 8.2

    incident.status = "ACTIVE"
    incident.excursion_temp_c = 8.2
    incident.drift_rate_c_per_min = 0.22
    incident.time_to_spoilage_minutes = 102

    # Reset plans to recommended
    plans = db.query(models.RecoveryPlan).filter(models.RecoveryPlan.incident_id == incident_id).all()
    for p in plans:
        p.status = "RECOMMENDED"
        p.approved_by = None
        p.approved_at = None

    db.commit()
    return {"success": True, "message": "Demo scenario reset to initial breach state (8.2°C, AC-2048)."}
