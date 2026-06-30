from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.metric import MetricCreate, MetricRead
from backend.app.services.incident_service import create_metric, list_metrics

router = APIRouter()


@router.post("", response_model=MetricRead)
def add_metric(metric_in: MetricCreate, db: Session = Depends(get_db)) -> MetricRead:
    return create_metric(db, metric_in)


@router.get("", response_model=list[MetricRead])
def get_metrics(
    db: Session = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)
) -> list[MetricRead]:
    return list_metrics(db, limit=limit)
