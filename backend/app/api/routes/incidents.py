from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.incident import IncidentRead, IncidentUpdate
from backend.app.schemas.rca import RCAResponse
from backend.app.services.incident_service import list_incidents, update_incident

router = APIRouter()


@router.get("", response_model=list[IncidentRead])
def get_incidents(
    db: Session = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)
) -> list[IncidentRead]:
    return list(list_incidents(db, limit=limit))


@router.patch("/{incident_id}", response_model=IncidentRead)
def patch_incident(
    incident_id: int, update: IncidentUpdate, db: Session = Depends(get_db)
) -> IncidentRead:
    incident = update_incident(db, incident_id, update)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.get("/{incident_id}/rca", response_model=RCAResponse)
def get_rca(incident_id: int, db: Session = Depends(get_db)) -> RCAResponse:
    """Return the stored Root Cause Analysis for an incident.

    Currently reads the root_cause / recommendation fields persisted on the
    Incident row at prediction time.  In Phase 5 this will be upgraded to
    call the LLM with full context and store a dedicated RCA record.
    """
    from sqlalchemy import select
    from backend.app.models.incident import Incident

    incident = db.execute(
        select(Incident).where(Incident.id == incident_id)
    ).scalar_one_or_none()

    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    return RCAResponse(
        incident_id=incident.id,
        root_cause=incident.root_cause,
        recommendation=incident.recommendation,
        rationale=incident.notes or "No additional rationale stored.",
        confidence=None,  # Will be populated in Phase 5 (LLM path)
        analyzed_at=incident.created_at,
    )
