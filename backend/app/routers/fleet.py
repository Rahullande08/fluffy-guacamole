from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/fleet", tags=["Fleet"])

@router.get("", response_model=List[schemas.VehicleOut])
def list_fleet(
    status: Optional[str] = Query(None, description="Filter by status: ALERT, NOMINAL, TRANSIT, DIVERTED"),
    cargo: Optional[str] = Query(None, description="Filter by cargo name keyword"),
    db: Session = Depends(get_db)
):
    """Retrieve all synchronized fleet vehicles with optional filtering."""
    query = db.query(models.Vehicle)
    if status:
        query = query.filter(models.Vehicle.status.ilike(f"%{status}%"))
    if cargo:
        query = query.filter(models.Vehicle.cargo_name.ilike(f"%{cargo}%"))
    return query.order_by(models.Vehicle.id.asc()).all()

@router.get("/{vehicle_id}", response_model=schemas.VehicleOut)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed metadata and current status for a specific vehicle."""
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")
    return vehicle

@router.get("/{vehicle_id}/readings", response_model=List[schemas.SensorReadingOut])
def get_vehicle_readings(
    vehicle_id: str,
    limit: int = Query(50, ge=1, le=200),
    sensor_code: Optional[str] = Query(None, description="Filter by sensor: T-04, T-01_AIR_RETURN, etc."),
    db: Session = Depends(get_db)
):
    """Retrieve historical sensor readings for telemetry drift and sparkline rendering."""
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_id} not found")

    query = db.query(models.SensorReading).filter(models.SensorReading.vehicle_id == vehicle_id)
    if sensor_code:
        query = query.filter(models.SensorReading.sensor_code == sensor_code)
    
    return query.order_by(models.SensorReading.timestamp.asc()).limit(limit).all()
