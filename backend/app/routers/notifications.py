from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(tags=["Notifications & Logs"])

@router.get("/notifications", response_model=List[schemas.NotificationOut])
def list_notifications(db: Session = Depends(get_db)):
    """Retrieve all operational alerts and notifications."""
    return db.query(models.Notification).order_by(models.Notification.timestamp.desc()).all()

@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    """Mark a notification as read."""
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"success": True}

@router.get("/activity-logs")
def list_activity_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve system event ledger records for the audit timeline."""
    logs = db.query(models.ActivityLog).order_by(models.ActivityLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "event_type": l.event_type,
            "message": l.message,
            "vehicle_id": l.vehicle_id,
            "incident_id": l.incident_id,
            "user_name": l.user_name,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]
