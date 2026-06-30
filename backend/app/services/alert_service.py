"""CRUD service for Alert threshold rules."""
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.alert import Alert
from backend.app.schemas.alert import AlertCreate, AlertUpdate


def list_alerts(db: Session, limit: int = 100) -> Sequence[Alert]:
    return db.execute(
        select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    ).scalars().all()


def get_alert(db: Session, alert_id: int) -> Alert | None:
    return db.get(Alert, alert_id)


def create_alert(db: Session, alert_in: AlertCreate) -> Alert:
    alert = Alert(**alert_in.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def update_alert(db: Session, alert_id: int, update: AlertUpdate) -> Alert | None:
    alert = db.get(Alert, alert_id)
    if alert is None:
        return None
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, alert_id: int) -> bool:
    alert = db.get(Alert, alert_id)
    if alert is None:
        return False
    db.delete(alert)
    db.commit()
    return True


def list_active_alerts(db: Session) -> Sequence[Alert]:
    return db.execute(
        select(Alert).where(Alert.is_active.is_(True))
    ).scalars().all()
