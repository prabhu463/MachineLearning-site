"""Model registry API routes.

Endpoints
---------
GET  /api/v1/models               — list all registry entries
GET  /api/v1/models/active        — get the current active model
POST /api/v1/models/train         — trigger a training run (blocking, ~30 s)
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.model_registry import (
    ModelInfoResponse,
    ModelRegistryRead,
    TrainRequest,
    TrainResponse,
)
from backend.app.services.model_service import get_active_model, list_models, register_model

logger = logging.getLogger(__name__)
router = APIRouter()


# ── List all registry entries ─────────────────────────────────────────────────

@router.get("", response_model=list[ModelRegistryRead])
def get_models(db: Session = Depends(get_db), limit: int = 50) -> list[ModelRegistryRead]:
    return list(list_models(db, limit=limit))


# ── Get the active (champion) model entry ─────────────────────────────────────

@router.get("/active", response_model=ModelRegistryRead)
def get_active(db: Session = Depends(get_db)) -> ModelRegistryRead:
    entry = get_active_model(db)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active model found. Run POST /models/train first.",
        )
    return entry


# ── Trigger a training run ────────────────────────────────────────────────────

@router.post("/train", response_model=TrainResponse, status_code=status.HTTP_201_CREATED)
def train_model(body: TrainRequest, db: Session = Depends(get_db)) -> TrainResponse:
    """Generate synthetic data and train all candidate models.

    This is a *synchronous* endpoint — it blocks until training completes
    (typically 20–60 seconds depending on dataset size).  A background
    worker / async queue will be added in Phase 4.
    """
    logger.info("Training triggered via API — rows=%d  random_state=%d", body.rows, body.random_state)

    try:
        from ml.src.data_generation import save_raw_dataset
        from ml.src.training import train_models

        dataset_path = save_raw_dataset(rows=body.rows)
        artifact = train_models(dataset_path, random_state=body.random_state)
    except Exception as exc:
        logger.exception("Training run failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {exc}",
        ) from exc

    # Persist result to model registry
    entry = register_model(
        db,
        model_name=artifact.name,
        model_version=artifact.version,
        artifact_path=str(artifact.path),
        metrics=artifact.metrics,
    )

    # Invalidate the cached orchestrator so the next prediction loads the new model
    try:
        from backend.app.api.routes.predictions import _get_orchestrator
        _get_orchestrator.cache_clear()
        logger.info("Orchestrator cache cleared — new model will be loaded on next prediction")
    except Exception:  # noqa: BLE001
        pass

    return TrainResponse(
        model_name=artifact.name,
        version=artifact.version,
        artifact_path=str(artifact.path),
        metrics=artifact.metrics,
        registry_id=entry.id,
    )
