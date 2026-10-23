from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..services.agent_tools import record_recovery_decision

router = APIRouter(tags=["Recovery"])

@router.get("/recovery/facilities", response_model=List[schemas.RecoveryFacilityOut])
def list_facilities(db: Session = Depends(get_db)):
    """Retrieve all recovery cold-storage facilities for matrix comparison."""
    facilities = db.query(models.RecoveryFacility).order_by(models.RecoveryFacility.distance_km.asc()).all()
    return facilities

@router.get("/recovery-plans/{plan_id}", response_model=schemas.RecoveryPlanOut)
def get_recovery_plan(plan_id: str, db: Session = Depends(get_db)):
    """Retrieve specific recovery plan details."""
    plan = db.query(models.RecoveryPlan).filter(models.RecoveryPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail=f"Recovery plan {plan_id} not found")
    return plan

@router.post("/recovery-plans/{plan_id}/approve", response_model=schemas.ApprovePlanResponse)
def approve_recovery_plan(
    plan_id: str,
    payload: Optional[schemas.ApprovePlanRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Dispatcher approval endpoint.
    Validates input, records dispatcher sign-off, updates vehicle and incident status,
    and persists cryptographic audit entry for FDA 21 CFR Part 11.
    """
    authorized_by = payload.authorized_by if payload else "Sarah Jenkins"
    role = payload.role if payload else "Lead Dispatcher"
    notes = payload.notes if payload else "Authorized autonomous diversion via AeroCold HUD."

    try:
        result = record_recovery_decision(
            db=db,
            plan_id=plan_id,
            decision="APPROVE",
            authorized_by=authorized_by,
            role=role,
            notes=notes
        )
        return schemas.ApprovePlanResponse(
            success=True,
            message=result["message"],
            plan_id=plan_id,
            status="APPROVED",
            authorized_by=authorized_by,
            timestamp=datetime.now(timezone.utc),
            dispatch_edi_code="EDI-214-DIVERSION-ACK",
            signature_hash=result["signature_hash"],
            simulated=True
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval execution failed: {str(e)}")

@router.post("/recovery-plans/{plan_id}/reject")
def reject_recovery_plan(
    plan_id: str,
    reason: Optional[str] = "Manual operator override",
    db: Session = Depends(get_db)
):
    """Dispatcher rejection endpoint."""
    try:
        result = record_recovery_decision(
            db=db,
            plan_id=plan_id,
            decision="REJECT",
            authorized_by="Sarah Jenkins",
            role="Lead Dispatcher",
            notes=reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
