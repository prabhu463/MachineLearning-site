from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from backend.app.core.config import get_settings
from ml.src.constants import FEATURE_COLUMNS, LABEL_MAP


@dataclass
class PredictionResult:
    predicted_label: str
    risk_score: float
    confidence: float
    probabilities: dict[str, float]


class IncidentModelService:
    def __init__(self, artifact_path: Path | None = None) -> None:
        settings = get_settings()
        self.settings = settings
        self.artifact_path = artifact_path or self._resolve_artifact_path()
        self.bundle: dict[str, object] | None = None
        if self.artifact_path.exists():
            self.bundle = joblib.load(self.artifact_path)

    def _resolve_artifact_path(self) -> Path:
        """Resolve the model artifact path.

        Priority:
        1. ``best_model.json`` in reports_dir — use artifact_path as relative to project root.
        2. Default ``xgboost_model.joblib`` in model_dir.

        The path stored in ``best_model.json`` may be an absolute Windows path from
        a previous training run.  We extract only the filename and resolve it
        against model_dir so it works on any machine / container.
        """
        best_report = Path(self.settings.reports_dir) / "best_model.json"
        if best_report.exists():
            try:
                payload = json.loads(best_report.read_text())
                artifact = payload.get("artifact_path")
                if artifact:
                    # Accept both relative and absolute paths — always re-anchor to model_dir
                    filename = Path(artifact).name
                    candidate = Path(self.settings.model_dir) / filename
                    if candidate.exists():
                        return candidate
            except (json.JSONDecodeError, OSError):
                pass
        return Path(self.settings.model_dir) / "xgboost_model.joblib"

    def load(self) -> None:
        if self.artifact_path.exists():
            self.bundle = joblib.load(self.artifact_path)
        else:
            self.bundle = None

    def _heuristic_predict(self, payload: dict[str, float | int]) -> PredictionResult:
        cpu = float(payload["cpu_usage"])
        memory = float(payload["memory_usage"])
        latency = float(payload["network_latency_ms"])
        error_rate = float(payload["error_rate"])
        response_time = float(payload["response_time_ms"])
        traffic = float(payload["request_count"])

        critical_signal = min(
            1.0,
            (cpu / 100) * 0.35
            + (memory / 100) * 0.2
            + (latency / 600) * 0.2
            + error_rate * 0.15
            + min(traffic / 1500, 1.0) * 0.1,
        )
        warning_signal = min(
            1.0,
            (cpu / 100) * 0.25
            + (memory / 100) * 0.2
            + (response_time / 1200) * 0.25
            + error_rate * 0.2,
        )
        normal_signal = max(0.0, 1.0 - max(critical_signal, warning_signal))
        raw = np.array([normal_signal, warning_signal, critical_signal], dtype=float)
        if raw.sum() == 0:
            raw = np.array([0.7, 0.2, 0.1], dtype=float)
        proba = raw / raw.sum()
        index = int(np.argmax(proba))
        predicted_label = LABEL_MAP[index]
        confidence = float(proba[index])
        risk_score = float((proba[1] * 0.6) + (proba[2] * 1.0))
        return PredictionResult(
            predicted_label=predicted_label,
            risk_score=risk_score,
            confidence=confidence,
            probabilities={LABEL_MAP[i]: float(probability) for i, probability in enumerate(proba)},
        )

    def _build_feature_frame(self, payload: dict[str, float | int]) -> pd.DataFrame:
        cpu_usage = float(payload["cpu_usage"])
        memory_usage = float(payload["memory_usage"])
        error_rate = float(payload["error_rate"])
        network_latency_ms = float(payload["network_latency_ms"])
        response_time_ms = float(payload["response_time_ms"])

        enriched_payload = dict(payload)
        enriched_payload["rolling_cpu_mean"] = cpu_usage
        enriched_payload["rolling_memory_mean"] = memory_usage
        enriched_payload["rolling_error_mean"] = error_rate
        enriched_payload["latency_to_response_ratio"] = network_latency_ms / (response_time_ms + 1e-6)
        return pd.DataFrame([enriched_payload])[FEATURE_COLUMNS]

    def predict(self, payload: dict[str, float | int]) -> PredictionResult:
        if self.bundle is None:
            self.load()
        if self.bundle is None:
            return self._heuristic_predict(payload)
        model = self.bundle["model"]
        features = self._build_feature_frame(payload)
        proba = model.predict_proba(features)[0]
        index = int(np.argmax(proba))
        predicted_label = LABEL_MAP[index]
        confidence = float(proba[index])
        risk_score = float((proba[1] * 0.6) + (proba[2] * 1.0))
        return PredictionResult(
            predicted_label=predicted_label,
            risk_score=risk_score,
            confidence=confidence,
            probabilities={LABEL_MAP[i]: float(probability) for i, probability in enumerate(proba)},
        )
