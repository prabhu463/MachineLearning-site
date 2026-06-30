from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.dashboard import DashboardSummary
from backend.app.services.incident_service import incident_summary, latest_incident, latest_metric

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)) -> DashboardSummary:
    stats = incident_summary(db)
    return DashboardSummary(
        **stats,
        latest_metric=latest_metric(db),
        latest_incident=latest_incident(db),
    )
