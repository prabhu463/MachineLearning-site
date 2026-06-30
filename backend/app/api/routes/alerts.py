"""Alert rules API endpoints.

GET    /api/v1/alerts         — list all alert rules
POST   /api/v1/alerts         — create a new alert rule
GET    /api/v1/alerts/{id}    — get a single rule
PATCH  /api/v1/alerts/{id}    — update threshold / active state
DELETE /api/v1/alerts/{id}    — remove a rule
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.alert import AlertCreate, AlertRead, AlertUpdate
from backend.app.services.alert_service import (
    create_alert,
    delete_alert,
    get_alert,
    list_alerts,
    update_alert,
)

router = APIRouter()


@router.get("", response_model=list[AlertRead])
def get_alerts(
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[AlertRead]:
    return list(list_alerts(db, limit=limit))


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def add_alert(alert_in: AlertCreate, db: Session = Depends(get_db)) -> AlertRead:
    return create_alert(db, alert_in)


@router.get("/{alert_id}", response_model=AlertRead)
def get_single_alert(alert_id: int, db: Session = Depends(get_db)) -> AlertRead:
    alert = get_alert(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.patch("/{alert_id}", response_model=AlertRead)
def patch_alert(
    alert_id: int, update: AlertUpdate, db: Session = Depends(get_db)
) -> AlertRead:
    alert = update_alert(db, alert_id, update)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


from fastapi import Response

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_alert(alert_id: int, db: Session = Depends(get_db)) -> Response:
    if not delete_alert(db, alert_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
