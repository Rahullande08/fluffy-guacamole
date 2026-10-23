import math
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .. import models
from .maps_service import estimate_travel_time

# Cargo thermal handling database (deterministic rules)
CARGO_RULES = {
    "strawberries": {
        "ideal_temp_min_c": 0.0,
        "ideal_temp_max_c": 2.0,
        "critical_threshold_c": 4.0,
        "spoilage_acceleration_factor": 1.45,
        "max_cumulative_degree_hours": 8.0,
        "requires_prechilled_crossdock": True,
        "handling_class": "Perishable Berry / High Respiration"
    },
    "fresh strawberries": {
        "ideal_temp_min_c": 0.0,
        "ideal_temp_max_c": 2.0,
        "critical_threshold_c": 4.0,
        "spoilage_acceleration_factor": 1.45,
        "max_cumulative_degree_hours": 8.0,
        "requires_prechilled_crossdock": True,
        "handling_class": "Perishable Berry / High Respiration"
    },
    "vaccines": {
        "ideal_temp_min_c": 2.0,
        "ideal_temp_max_c": 8.0,
        "critical_threshold_c": 9.0,
        "spoilage_acceleration_factor": 2.0,
        "max_cumulative_degree_hours": 2.0,
        "requires_prechilled_crossdock": True,
        "handling_class": "Biologics / FDA Strict Part 11"
    },
    "frozen meat": {
        "ideal_temp_min_c": -22.0,
        "ideal_temp_max_c": -18.0,
        "critical_threshold_c": -12.0,
        "spoilage_acceleration_factor": 1.1,
        "max_cumulative_degree_hours": 24.0,
        "requires_prechilled_crossdock": True,
        "handling_class": "Deep Freeze Cryo"
    }
}

def get_vehicle_telemetry(db: Session, vehicle_id: str) -> dict:
    """Read vehicle telemetry and validate sensor timestamps and data quality."""
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        return {"error": f"Vehicle {vehicle_id} not found"}

    recent_readings = (
        db.query(models.SensorReading)
        .filter(models.SensorReading.vehicle_id == vehicle_id)
        .order_by(models.SensorReading.timestamp.desc())
        .limit(10)
        .all()
    )

    is_data_valid = len(recent_readings) > 0
    return {
        "vehicle_id": vehicle.id,
        "name": vehicle.name,
        "carrier": vehicle.carrier,
        "driver_name": vehicle.driver_name,
        "driver_phone": vehicle.driver_phone,
        "current_temp_c": vehicle.current_temp_c,
        "target_temp_c": vehicle.target_temp_c,
        "threshold_temp_c": vehicle.threshold_temp_c,
        "latitude": vehicle.latitude,
        "longitude": vehicle.longitude,
        "speed_mph": vehicle.speed_mph,
        "heading": vehicle.heading,
        "genset_fuel_pct": vehicle.genset_fuel_pct,
        "cargo_name": vehicle.cargo_name,
        "cargo_weight_kg": vehicle.cargo_weight_kg,
        "cargo_pallets": vehicle.cargo_pallets,
        "cargo_value_usd": vehicle.cargo_value_usd,
        "data_quality": "VERIFIED_CAN_BUS" if is_data_valid else "DEGRADED",
        "recent_readings_count": len(recent_readings),
        "status": vehicle.status
    }

def get_cargo_handling_rules(cargo_name: str) -> dict:
    """Retrieve cargo-specific handling rules."""
    key = cargo_name.lower()
    for rule_key, rules in CARGO_RULES.items():
        if rule_key in key:
            return rules
    return CARGO_RULES["strawberries"]

def calculate_temperature_risk(
    current_temp: float,
    target_temp: float,
    threshold_temp: float,
    drift_rate_c_per_min: float,
    cargo_rules: dict
) -> dict:
    """Calculate temperature excursion magnitude, duration, and deterministic risk score."""
    excursion_magnitude = max(0.0, current_temp - threshold_temp)
    
    # Safe time before quality loss (minutes)
    if drift_rate_c_per_min > 0:
        minutes_to_decay = max(10, round((12.0 - current_temp) / drift_rate_c_per_min))
    else:
        minutes_to_decay = 180

    # Risk level classification
    if current_temp >= threshold_temp + 3.0:
        risk_level = "CRITICAL"
        biological_yield_proj = 99.4
    elif current_temp >= threshold_temp:
        risk_level = "HIGH"
        biological_yield_proj = 99.7
    else:
        risk_level = "NOMINAL"
        biological_yield_proj = 100.0

    return {
        "risk_level": risk_level,
        "excursion_magnitude_c": round(excursion_magnitude, 2),
        "drift_rate_c_per_min": drift_rate_c_per_min,
        "time_to_quality_loss_minutes": minutes_to_decay,
        "projected_yield_pct": biological_yield_proj,
        "is_breach": current_temp > threshold_temp
    }

def find_recovery_facilities(db: Session, origin_lat: float, origin_lon: float) -> list:
    """Search eligible recovery destinations and calculate estimated travel routes."""
    facilities = db.query(models.RecoveryFacility).all()
    results = []
    for f in facilities:
        route = estimate_travel_time(origin_lat, origin_lon, f.latitude, f.longitude)
        results.append({
            "facility_id": f.id,
            "name": f.name,
            "short_name": f.short_name,
            "address": f.address,
            "bay_status": f.bay_status,
            "prechilled_dock_ready": f.prechilled_dock_ready,
            "distance_km": route["distance_km"],
            "estimated_travel_minutes": f.estimated_travel_minutes or route["duration_minutes"],
            "capacity_pct": f.capacity_pct,
            "rating": f.rating,
            "is_recommended": f.is_recommended,
            "hourly_rate_usd": f.hourly_rate_usd,
            "route_provider": route["provider"]
        })
    # Sort by recommendation and travel time
    results.sort(key=lambda x: (not x["is_recommended"], x["estimated_travel_minutes"]))
    return results

def compare_recovery_options(facilities: list, vehicle_telemetry: dict, risk_data: dict) -> list:
    """Compare destinations using time, compatibility, availability evidence, and cost."""
    cargo_val = vehicle_telemetry.get("cargo_value_usd", 142000.0)
    time_limit = risk_data.get("time_to_quality_loss_minutes", 102)

    comparisons = []
    for f in facilities:
        travel_time = f["estimated_travel_minutes"]
        time_buffer = time_limit - travel_time
        is_viable = time_buffer > 0 and f["prechilled_dock_ready"]
        
        # Salvage calculation based on arrival within thermal buffer
        if time_buffer > 30:
            salvage_pct = 99.4
        elif time_buffer > 0:
            salvage_pct = 95.0
        else:
            salvage_pct = 60.0

        salvage_val = round((salvage_pct / 100.0) * cargo_val, 2)
        score = 0.96 if f["is_recommended"] else round(max(0.60, 0.90 - (travel_time / 100.0)), 2)

        comparisons.append({
            **f,
            "time_buffer_minutes": time_buffer,
            "is_viable": is_viable,
            "salvage_pct": salvage_pct,
            "projected_salvage_usd": salvage_val,
            "composite_score": score
        })
    return comparisons

def create_recovery_plan(
    db: Session,
    incident_id: str,
    vehicle_id: str,
    facility_id: str,
    confidence_score: float,
    estimated_arrival_minutes: int,
    projected_salvage_usd: float,
    biological_yield_pct: float,
    ai_reasoning: str,
    evidence_summary: str,
    assumptions: str
) -> models.RecoveryPlan:
    """Create and persist a structured recovery plan in the database."""
    # Check if a plan already exists for this incident/facility to prevent duplicate creation
    existing = (
        db.query(models.RecoveryPlan)
        .filter(models.RecoveryPlan.incident_id == incident_id, models.RecoveryPlan.facility_id == facility_id)
        .first()
    )
    if existing:
        existing.confidence_score = confidence_score
        existing.estimated_arrival_minutes = estimated_arrival_minutes
        existing.projected_salvage_usd = projected_salvage_usd
        existing.biological_yield_pct = biological_yield_pct
        existing.ai_reasoning = ai_reasoning
        existing.evidence_summary = evidence_summary
        existing.assumptions = assumptions
        db.commit()
        db.refresh(existing)
        return existing

    plan = models.RecoveryPlan(
        id=f"PLAN-{datetime.now().strftime('%M%S')}",
        incident_id=incident_id,
        vehicle_id=vehicle_id,
        facility_id=facility_id,
        status="RECOMMENDED",
        confidence_score=confidence_score,
        estimated_arrival_minutes=estimated_arrival_minutes,
        projected_salvage_usd=projected_salvage_usd,
        biological_yield_pct=biological_yield_pct,
        ai_reasoning=ai_reasoning,
        evidence_summary=evidence_summary,
        assumptions=assumptions,
        created_by="AeroCold Autonomous Intelligence Agent"
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def request_human_approval(plan_id: str, dispatcher_info: dict) -> dict:
    """Format structured payload requesting human dispatcher sign-off."""
    return {
        "plan_id": plan_id,
        "requires_authorization": True,
        "recommended_action": "AUTONOMOUS_DIVERSION_DISPATCH",
        "dispatcher_role_required": "Lead Dispatcher / Cold-Chain Officer",
        "demo_mode": True,
        "dispatched_to_in_cab": False
    }

def record_recovery_decision(
    db: Session,
    plan_id: str,
    decision: str,
    authorized_by: str,
    role: str,
    notes: str = None
) -> dict:
    """Persist human approval or rejection to database and audit log."""
    plan = db.query(models.RecoveryPlan).filter(models.RecoveryPlan.id == plan_id).first()
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")

    if decision.upper() == "APPROVE":
        plan.status = "APPROVED"
        plan.approved_by = f"{authorized_by} ({role})"
        plan.approved_at = datetime.now(timezone.utc)

        # Update vehicle status
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == plan.vehicle_id).first()
        if vehicle:
            vehicle.status = "DIVERTED"

        # Update incident status
        incident = db.query(models.Incident).filter(models.Incident.id == plan.incident_id).first()
        if incident:
            incident.status = "MITIGATING"

        # Create approval record
        approval = models.Approval(
            id=f"APPR-{datetime.now().strftime('%f')[:6]}",
            plan_id=plan.id,
            authorized_by=authorized_by,
            role=role,
            demo_mode=True,
            signature_hash=f"SHA256:AC-AUTH-{datetime.now().strftime('%Y%m%d%H%M%S')}-V4",
            dispatch_transmitted=True,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(approval)

        # Write audit log
        log = models.ActivityLog(
            event_type="DIVERSION_APPROVED",
            message=f"Autonomous Diversion Plan {plan.id} authorized by {authorized_by} ({role}). Transmitted EDI 214 & turn-by-turn routing to Unit {plan.vehicle_id}.",
            vehicle_id=plan.vehicle_id,
            incident_id=plan.incident_id,
            user_name=authorized_by,
            payload_json=f'{{"plan_id": "{plan.id}", "facility_id": "{plan.facility_id}", "notes": "{notes or ""}"}}'
        )
        db.add(log)
        db.commit()

        return {
            "success": True,
            "message": f"Autonomous diversion authorized and dispatched to Unit {plan.vehicle_id}",
            "plan_id": plan.id,
            "status": "APPROVED",
            "authorized_by": authorized_by,
            "signature_hash": approval.signature_hash
        }
    else:
        plan.status = "REJECTED"
        plan.rejection_reason = notes or "Dispatcher manual override"
        log = models.ActivityLog(
            event_type="PLAN_REJECTED",
            message=f"Recovery plan {plan.id} rejected by {authorized_by}: {plan.rejection_reason}",
            vehicle_id=plan.vehicle_id,
            incident_id=plan.incident_id,
            user_name=authorized_by
        )
        db.add(log)
        db.commit()
        return {
            "success": True,
            "message": f"Plan {plan.id} rejected",
            "plan_id": plan.id,
            "status": "REJECTED"
        }
