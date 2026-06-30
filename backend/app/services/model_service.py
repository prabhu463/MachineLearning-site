"""Model registry service — DB-level CRUD for ModelRegistry rows."""
from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.model_registry import ModelRegistry


def list_models(db: Session, limit: int = 50) -> Sequence[ModelRegistry]:
    stmt = select(ModelRegistry).order_by(ModelRegistry.created_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def get_active_model(db: Session) -> ModelRegistry | None:
    stmt = (
        select(ModelRegistry)
        .where(ModelRegistry.is_active.is_(True))
        .order_by(ModelRegistry.created_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def register_model(
    db: Session,
    model_name: str,
    model_version: str,
    artifact_path: str,
    metrics: dict[str, float],
) -> ModelRegistry:
    """Deactivate all existing entries, then insert the new active model."""
    # Mark all previous entries inactive
    for existing in db.execute(select(ModelRegistry)).scalars().all():
        existing.is_active = False
    db.flush()

    entry = ModelRegistry(
        model_name=model_name,
        model_version=model_version,
        artifact_path=artifact_path,
        metrics_json=json.dumps(metrics),
        is_active=True,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
