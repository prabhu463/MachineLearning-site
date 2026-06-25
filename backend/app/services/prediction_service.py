from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.schemas.action import ActionCreate
from backend.app.schemas.incident import IncidentCreate
from backend.app.schemas.prediction import PredictionRequest
from backend.app.services.incident_service import (
    create_action,
    create_incident,
    create_metric,
)
from backend.app.services.remediation import build_actions, execute_action
from backend.app.services.root_cause import RootCauseAnalyzer
from ml.src.inference import IncidentModelService


class PredictionOrchestrator:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.model_service = IncidentModelService()
        self.root_cause = RootCauseAnalyzer(settings.root_cause_api_key, settings.root_cause_model)

    def predict(self, db: Session, payload: PredictionRequest, auto_execute: bool = False) -> dict[str, object]:
        metric = create_metric(db, payload)
        model_result = self.model_service.predict(payload.model_dump())
        root_cause_result = self.root_cause.analyze(payload.model_dump())
        severity = "critical" if model_result.risk_score >= 0.8 else "warning" if model_result.risk_score >= 0.55 else "info"
        incident = None
        actions: list[dict[str, str]] = []

        if model_result.risk_score >= self.settings.risk_threshold:
            incident = create_incident(
                db,
                IncidentCreate(
                    metric_id=metric.id,
                    severity=severity,
                    risk_score=model_result.risk_score,
                    predicted_label=model_result.predicted_label,
                    root_cause=root_cause_result.root_cause,
                    recommendation=root_cause_result.recommendation,
                    notes=root_cause_result.rationale,
                ),
            )
            if auto_execute:
                for action_name in build_actions(root_cause_result.recommendation, severity):
                    action_result = execute_action(action_name, incident.id, mode="simulate")
                    action = create_action(
                        db,
                        ActionCreate(
                            incident_id=incident.id,
                            action_name=action_name,
                            executed_by="automation-bot",
                            details=action_result["details"],
                        ),
                        status=action_result["status"],
                    )
                    actions.append(
                        {
                            "id": str(action.id),
                            "action_name": action.action_name,
                            "status": action.status,
                            "details": action.details,
                        }
                    )

        return {
            "metric_id": metric.id,
            "predicted_label": model_result.predicted_label,
            "risk_score": model_result.risk_score,
            "confidence": model_result.confidence,
            "probabilities": model_result.probabilities,
            "root_cause": root_cause_result.root_cause,
            "recommendation": root_cause_result.recommendation,
            "rationale": root_cause_result.rationale,
            "incident_created": incident is not None,
            "incident": incident,
            "actions": actions,
            "created_at": datetime.now(timezone.utc),
        }
