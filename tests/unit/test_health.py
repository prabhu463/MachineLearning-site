"""Unit tests for the health endpoint helper functions."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from backend.app.api.routes.health import _ml_model_status


def test_ml_model_status_missing_when_no_files(tmp_path: Path):
    """Returns 'missing' when model_dir has no .joblib files."""
    with patch("backend.app.api.routes.health.get_settings") as mock_settings:
        mock_settings.return_value.model_dir = str(tmp_path / "models")
        mock_settings.return_value.reports_dir = str(tmp_path / "reports")
        status = _ml_model_status()
    assert status == "missing"


def test_ml_model_status_ok_when_joblib_present(tmp_path: Path):
    """Returns 'ok' when a .joblib file exists in model_dir."""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "xgboost_model.joblib").write_bytes(b"dummy")
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()

    with patch("backend.app.api.routes.health.get_settings") as mock_settings:
        mock_settings.return_value.model_dir = str(model_dir)
        mock_settings.return_value.reports_dir = str(reports_dir)
        status = _ml_model_status()
    assert status == "ok"
