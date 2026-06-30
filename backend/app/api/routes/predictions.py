from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db
from backend.app.schemas.model_registry import ModelInfoResponse
from backend.app.schemas.prediction import PredictionRequest, PredictionResponse
from backend.app.services.prediction_service import PredictionOrchestrator

router = APIRouter()


@lru_cache(maxsize=1)
def _get_orchestrator() -> PredictionOrchestrator:
    """Lazily initialise the ML orchestrator once and cache it.

    Deferring construction to first request means a missing model file will
    raise an error for that request only — it won't crash the entire app at
    import time.
    """
    return PredictionOrchestrator()


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    """Return metadata about the currently loaded ML model.

    Reads ``best_model.json`` from the reports directory; no DB lookup needed.
    If the report or artifact is missing, returns is_loaded=False with empty metrics.
    """
    settings = get_settings()
    best_report = Path(settings.reports_dir) / "best_model.json"

    if best_report.exists():
        try:
            payload = json.loads(best_report.read_text())
            artifact_filename = Path(payload.get("artifact_path", "")).name
            artifact_path = Path(settings.model_dir) / artifact_filename
            is_loaded = artifact_path.exists()
            from ml.src.constants import FEATURE_COLUMNS
            return ModelInfoResponse(
                model_name=payload.get("model_name", "unknown"),
                artifact_path=str(artifact_path),
                is_loaded=is_loaded,
                metrics=payload.get("metrics", {}),
                feature_columns=FEATURE_COLUMNS,
            )
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    # Fallback — no report present yet
    from ml.src.constants import FEATURE_COLUMNS
    return ModelInfoResponse(
        model_name="none",
        artifact_path="",
        is_loaded=False,
        metrics={},
        feature_columns=FEATURE_COLUMNS,
    )


@router.post("", response_model=PredictionResponse)
def predict(
    prediction_in: PredictionRequest,
    auto_execute: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    result = _get_orchestrator().predict(db, prediction_in, auto_execute=auto_execute)
    # Extract incident_id as a plain int *inside* the session scope (Fix #7).
    # Accessing ORM attributes after the session closes causes DetachedInstanceError.
    incident_id: int | None = result["incident"].id if result["incident"] else None
    return PredictionResponse(
        predicted_label=result["predicted_label"],
        risk_score=result["risk_score"],
        confidence=result["confidence"],
        root_cause=result["root_cause"],
        recommendation=result["recommendation"],
        incident_created=result["incident_created"],
        incident_id=incident_id,
        created_at=result["created_at"],
    )
