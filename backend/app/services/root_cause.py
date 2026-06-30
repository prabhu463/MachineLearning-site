from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class RootCauseResult:
    root_cause: str
    recommendation: str
    rationale: str


class RootCauseAnalyzer:
    def __init__(self, api_key: str | None, model: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.model = model
        if api_key:
            kwargs: dict = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self.client: OpenAI | None = OpenAI(**kwargs)
        else:
            self.client = None


    def heuristic_analysis(self, metrics: dict[str, float | int]) -> RootCauseResult:
        cpu = float(metrics["cpu_usage"])
        memory = float(metrics["memory_usage"])
        latency = float(metrics["network_latency_ms"])
        error_rate = float(metrics["error_rate"])
        request_count = int(metrics["request_count"])
        response_time = float(metrics["response_time_ms"])

        if memory > 85 and cpu > 65:
            return RootCauseResult(
                root_cause="Memory leak suspected",
                recommendation="Restart service and inspect heap growth.",
                rationale="Sustained memory pressure combined with high CPU suggests a leaking process.",
            )
        if latency > 320 and response_time > 500:
            return RootCauseResult(
                root_cause="Database latency spike",
                recommendation="Check DB connections, cache hot queries, and add resources.",
                rationale="Network and response latency aligned with backend slowdown.",
            )
        if request_count > 900 and latency > 250:
            return RootCauseResult(
                root_cause="Excessive request traffic",
                recommendation="Scale application replicas and enable rate limiting.",
                rationale="High throughput and latency often indicate traffic saturation.",
            )
        if error_rate > 0.15:
            return RootCauseResult(
                root_cause="Service crash pattern detected",
                recommendation="Restart service, inspect logs, and roll back recent deployment.",
                rationale="Error bursts frequently follow unstable releases or service failures.",
            )
        if cpu > 80:
            return RootCauseResult(
                root_cause="High CPU consumption",
                recommendation="Scale up compute or optimize expensive code paths.",
                rationale="CPU saturation is the dominant abnormality.",
            )
        return RootCauseResult(
            root_cause="No clear anomaly",
            recommendation="Continue monitoring and collect more telemetry.",
            rationale="Observed metrics are within normal operational ranges.",
        )

    def analyze(self, metrics: dict[str, float | int]) -> RootCauseResult:
        if not self.client:
            return self.heuristic_analysis(metrics)

        prompt = {
            "metrics": metrics,
            "task": "Identify likely root cause and actionable remediation for the incident.",
        }
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an SRE assistant. Return strict JSON with keys "
                            "root_cause, recommendation, rationale."
                        ),
                    },
                    {"role": "user", "content": json.dumps(prompt)},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            return RootCauseResult(
                root_cause=parsed.get("root_cause", "Unknown root cause"),
                recommendation=parsed.get("recommendation", "Investigate service health."),
                rationale=parsed.get("rationale", "LLM provided analysis."),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLM root cause analysis failed: %s", exc)
            return self.heuristic_analysis(metrics)
