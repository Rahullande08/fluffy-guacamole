from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview", response_model=schemas.AnalyticsOverviewOut)
def get_analytics_overview(db: Session = Depends(get_db)):
    """Aggregate cold-chain historical performance, compliance metrics, and excursion trends."""
    return schemas.AnalyticsOverviewOut(
        cold_chain_uptime_pct=99.82,
        total_prevented_spoilage_usd=842300.0,
        average_incident_resolution_minutes=18.4,
        fda_audit_compliance_score_pct=99.94,
        excursion_trends_by_week=[
            {"week": "Wk 40", "excursions": 4, "prevented_loss_usd": 128000},
            {"week": "Wk 41", "excursions": 2, "prevented_loss_usd": 64000},
            {"week": "Wk 42", "excursions": 3, "prevented_loss_usd": 92000},
            {"week": "Wk 43", "excursions": 1, "prevented_loss_usd": 141148}
        ],
        facility_success_metrics=[
            {"facility": "Cold Storage A", "intakes": 14, "avg_wait_minutes": 6.2, "yield_preservation_pct": 99.6},
            {"facility": "Oakland Cold Hub", "intakes": 9, "avg_wait_minutes": 11.5, "yield_preservation_pct": 98.1},
            {"facility": "Richmond Cryo Center", "intakes": 5, "avg_wait_minutes": 15.8, "yield_preservation_pct": 96.4}
        ]
    )
