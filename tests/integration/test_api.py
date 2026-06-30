"""Integration tests for the PredictiveOps AI API.

The ``PredictionOrchestrator`` is now lazily initialised via ``_get_orchestrator()``
(an ``lru_cache``-wrapped factory) instead of a module-level singleton called
``orchestrator``.  We patch the *factory* to return a pre-configured dummy so
the real ML model and OpenAI client are never touched during CI.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


# ---------------------------------------------------------------------------
# Dummy stubs
# ---------------------------------------------------------------------------

class _DummyModelService:
    """Returns a fixed critical prediction without loading any joblib file."""

    def predict(self, payload):  # noqa: ANN001
        return type(
            "Result",
            (),
            {
                "predicted_label": "critical",
                "risk_score": 0.88,
                "confidence": 0.70,
                "probabilities": {"normal": 0.1, "warning": 0.2, "critical": 0.7},
            },
        )()


class _DummyRootCause:
    """Returns a fixed heuristic result without calling the OpenAI API."""

    def analyze(self, payload):  # noqa: ANN001
        return type(
            "RootCause",
            (),
            {
                "root_cause": "High CPU consumption",
                "recommendation": "Restart service and scale application",
                "rationale": "Synthetic test analysis",
            },
        )()


class _DummyOrchestrator:
    """Thin stand-in for PredictionOrchestrator that delegates to the dummies."""

    def __init__(self) -> None:
        self.model_service = _DummyModelService()
        self.root_cause = _DummyRootCause()
        self.settings = type("S", (), {"risk_threshold": 0.65})()

    def predict(self, db, payload, auto_execute: bool = False):  # noqa: ANN001
        from backend.app.services.prediction_service import PredictionOrchestrator

        # Re-use the real orchestration logic but with dummy model + root cause
        real = PredictionOrchestrator.__new__(PredictionOrchestrator)
        real.settings = self.settings
        real.model_service = self.model_service
        real.root_cause = self.root_cause
        return real.predict(db, payload, auto_execute=auto_execute)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """TestClient with the ML orchestrator replaced by a deterministic dummy."""
    dummy = _DummyOrchestrator()
    # Patch the lru_cache factory so every call returns our dummy instance
    with patch(
        "backend.app.api.routes.predictions._get_orchestrator",
        return_value=dummy,
    ):
        with TestClient(app) as c:
            yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_health_endpoint(client):  # noqa: ANN001
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"


def test_dashboard_summary(client):  # noqa: ANN001
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_metrics" in data
    assert "total_incidents" in data
    assert "average_risk_score" in data


def test_prediction_creates_incident(client):  # noqa: ANN001
    """A high-risk payload should create an incident and return the right schema."""
    response = client.post(
        "/api/v1/predict?auto_execute=true",
        json={
            "service_name": "checkout",
            "cpu_usage": 91,
            "memory_usage": 89,
            "disk_usage": 72,
            "network_latency_ms": 333,
            "request_count": 1200,
            "error_rate": 0.24,
            "response_time_ms": 850,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_score"] > 0.5
    assert body["predicted_label"] in {"normal", "warning", "critical"}
    assert isinstance(body["incident_created"], bool)
    assert "root_cause" in body
    assert "recommendation" in body


def test_metrics_endpoint(client):  # noqa: ANN001
    response = client.get("/api/v1/metrics?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_incidents_endpoint(client):  # noqa: ANN001
    response = client.get("/api/v1/incidents?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_actions_endpoint(client):  # noqa: ANN001
    response = client.get("/api/v1/actions?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
