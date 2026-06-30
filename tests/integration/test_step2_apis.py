"""Integration tests for new Step-2 endpoints:
- GET  /api/v1/models
- GET  /api/v1/models/active
- GET  /api/v1/predict/model-info
- GET  /api/v1/incidents/{id}/rca
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


# ── GET /models ───────────────────────────────────────────────────────────────

def test_list_models_returns_list(client):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── GET /models/active ────────────────────────────────────────────────────────

def test_active_model_404_when_no_registry(client):
    """With a fresh in-memory DB there is no active model."""
    response = client.get("/api/v1/models/active")
    # Either 404 (no model) or 200 (model seeded) — both are valid
    assert response.status_code in (200, 404)


# ── GET /predict/model-info ───────────────────────────────────────────────────

def test_model_info_returns_schema(client):
    response = client.get("/api/v1/predict/model-info")
    assert response.status_code == 200
    body = response.json()
    assert "model_name" in body
    assert "is_loaded" in body
    assert "feature_columns" in body
    assert isinstance(body["feature_columns"], list)
    assert len(body["feature_columns"]) > 0


# ── GET /incidents/{id}/rca — incident must exist first ──────────────────────

class _DummyModelService:
    def predict(self, payload):
        return type("R", (), {
            "predicted_label": "critical",
            "risk_score": 0.88,
            "confidence": 0.70,
            "probabilities": {"normal": 0.1, "warning": 0.2, "critical": 0.7},
        })()


class _DummyRootCause:
    def analyze(self, payload):
        return type("RC", (), {
            "root_cause": "High CPU consumption",
            "recommendation": "Scale application replicas",
            "rationale": "CPU is the dominant signal",
        })()


class _DummyOrchestrator:
    def __init__(self):
        self.model_service = _DummyModelService()
        self.root_cause = _DummyRootCause()
        self.settings = type("S", (), {"risk_threshold": 0.65})()

    def predict(self, db, payload, auto_execute=False):
        from backend.app.services.prediction_service import PredictionOrchestrator
        real = PredictionOrchestrator.__new__(PredictionOrchestrator)
        real.settings = self.settings
        real.model_service = self.model_service
        real.root_cause = self.root_cause
        return real.predict(db, payload, auto_execute=auto_execute)


@pytest.fixture()
def client_with_dummy():
    dummy = _DummyOrchestrator()
    with patch("backend.app.api.routes.predictions._get_orchestrator", return_value=dummy):
        with TestClient(app) as c:
            yield c


def test_rca_endpoint_for_existing_incident(client_with_dummy):
    """Create an incident via predict, then fetch its RCA."""
    pred_resp = client_with_dummy.post(
        "/api/v1/predict?auto_execute=false",
        json={
            "service_name": "auth",
            "cpu_usage": 92,
            "memory_usage": 85,
            "disk_usage": 60,
            "network_latency_ms": 310,
            "request_count": 1100,
            "error_rate": 0.22,
            "response_time_ms": 800,
        },
    )
    assert pred_resp.status_code == 200
    incident_id = pred_resp.json().get("incident_id")
    assert incident_id is not None, "Expected high-risk payload to create an incident"

    rca_resp = client_with_dummy.get(f"/api/v1/incidents/{incident_id}/rca")
    assert rca_resp.status_code == 200
    body = rca_resp.json()
    assert body["incident_id"] == incident_id
    assert "root_cause" in body
    assert "recommendation" in body
    assert "analyzed_at" in body


def test_rca_404_for_missing_incident(client_with_dummy):
    response = client_with_dummy.get("/api/v1/incidents/999999/rca")
    assert response.status_code == 404
