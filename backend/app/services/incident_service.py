from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from backend.app.models.action import ActionEvent
from backend.app.models.incident import Incident
from backend.app.models.metric import Metric
from backend.app.models.model_registry import ModelRegistry
from backend.app.schemas.action import ActionCreate
from backend.app.schemas.incident import IncidentCreate, IncidentUpdate
from backend.app.schemas.metric import MetricCreate


def create_metric(db: Session, metric_in: MetricCreate) -> Metric:
    metric = Metric(**metric_in.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def list_metrics(db: Session, limit: int = 100) -> Sequence[Metric]:
    stmt: Select[tuple[Metric]] = select(Metric).order_by(Metric.created_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def create_incident(db: Session, incident_in: IncidentCreate) -> Incident:
    incident = Incident(**incident_in.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def list_incidents(db: Session, limit: int = 100) -> Sequence[Incident]:
    stmt = select(Incident).order_by(Incident.created_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def update_incident(db: Session, incident_id: int, update: IncidentUpdate) -> Incident | None:
    incident = db.get(Incident, incident_id)
    if incident is None:
        return None
    incident.status = update.status
    incident.notes = update.notes
    db.commit()
    db.refresh(incident)
    return incident


def create_action(db: Session, action_in: ActionCreate, status: str) -> ActionEvent:
    action = ActionEvent(**action_in.model_dump(), status=status)
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def list_actions(db: Session, limit: int = 100) -> Sequence[ActionEvent]:
    stmt = select(ActionEvent).order_by(ActionEvent.created_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def incident_summary(db: Session) -> dict[str, float | int]:
    total_metrics = db.scalar(select(func.count(Metric.id))) or 0
    total_incidents = db.scalar(select(func.count(Incident.id))) or 0
    open_incidents = db.scalar(select(func.count(Incident.id)).where(Incident.status == "open")) or 0
    critical_incidents = (
        db.scalar(select(func.count(Incident.id)).where(Incident.severity == "critical")) or 0
    )
    average_risk_score = db.scalar(select(func.avg(Incident.risk_score))) or 0.0
    return {
        "total_metrics": int(total_metrics),
        "total_incidents": int(total_incidents),
        "open_incidents": int(open_incidents),
        "critical_incidents": int(critical_incidents),
        "average_risk_score": float(average_risk_score),
    }


def latest_metric(db: Session) -> Metric | None:
    return db.execute(select(Metric).order_by(Metric.created_at.desc()).limit(1)).scalar_one_or_none()


def latest_incident(db: Session) -> Incident | None:
    return (
        db.execute(select(Incident).order_by(Incident.created_at.desc()).limit(1)).scalar_one_or_none()
    )


def register_model(db: Session, model_name: str, model_version: str, artifact_path: str, metrics_json: str) -> ModelRegistry:
    registry = ModelRegistry(
        model_name=model_name,
        model_version=model_version,
        artifact_path=artifact_path,
        metrics_json=metrics_json,
    )
    db.add(registry)
    db.commit()
    db.refresh(registry)
    return registry
