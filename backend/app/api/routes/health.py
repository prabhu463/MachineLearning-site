from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.db.session import get_db

router = APIRouter()


def _ml_model_status() -> str:
    """Return 'ok' if a trained model artifact exists on disk, else 'missing'."""
    settings = get_settings()
    # Check best_model.json first; fall back to default xgboost artifact
    best_report = Path(settings.reports_dir) / "best_model.json"
    if best_report.exists():
        import json
        try:
            payload = json.loads(best_report.read_text())
            artifact = payload.get("artifact_path", "")
            # Re-anchor to model_dir in case the stored path is absolute/stale
            candidate = Path(settings.model_dir) / Path(artifact).name
            if candidate.exists():
                return "ok"
        except (json.JSONDecodeError, OSError):
            pass
    # Fallback: look for any .joblib in model_dir
    model_dir = Path(settings.model_dir)
    if model_dir.exists() and any(model_dir.glob("*.joblib")):
        return "ok"
    return "missing"


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Return service health: database reachability and ML model presence."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:  # noqa: BLE001
        db_status = "unreachable"

    ml_status = _ml_model_status()

    overall = "ok" if db_status == "ok" else "degraded"

    return {
        "status": overall,
        "service": "PredictiveOps AI",
        "version": "1.0.0",
        "database": db_status,
        "ml_model": ml_status,
    }
