from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ml.src.constants import DATA_RAW_DIR


@dataclass
class SyntheticScenario:
    name: str
    cpu_shift: float
    memory_shift: float
    latency_shift: float
    error_shift: float
    request_shift: float
    label: int


SCENARIOS = [
    SyntheticScenario("normal", 0, 0, 0, 0, 0, 0),
    SyntheticScenario("warning_load", 14, 10, 15, 0.05, 30, 1),
    SyntheticScenario("memory_leak", 8, 26, 10, 0.03, 10, 1),   # warning: memory pressure builds gradually
    SyntheticScenario("traffic_spike", 18, 8, 20, 0.08, 90, 2),  # critical: sudden overload
    SyntheticScenario("db_latency", 10, 8, 45, 0.04, 15, 1),    # warning: elevated latency, not outage
]


def generate_metric_row(index: int) -> dict[str, float | int | str]:
    scenario = random.choices(
        SCENARIOS, weights=[0.52, 0.18, 0.12, 0.10, 0.08], k=1
    )[0]
    base_cpu = np.clip(np.random.normal(34, 12), 1, 98)
    base_memory = np.clip(np.random.normal(42, 11), 1, 98)
    base_disk = np.clip(np.random.normal(48, 13), 1, 98)
    base_latency = np.clip(np.random.normal(72, 24), 4, 600)
    base_requests = max(int(np.random.normal(520, 180)), 10)
    base_error_rate = np.clip(np.random.beta(2.2, 18), 0, 1)
    base_response = np.clip(np.random.normal(240, 90), 10, 2400)

    cpu = np.clip(base_cpu + scenario.cpu_shift + np.random.normal(0, 4), 0, 100)
    memory = np.clip(base_memory + scenario.memory_shift + np.random.normal(0, 3), 0, 100)
    disk = np.clip(base_disk + np.random.normal(0, 4), 0, 100)
    latency = np.clip(base_latency + scenario.latency_shift + np.random.normal(0, 15), 1, 2000)
    requests = max(int(base_requests + scenario.request_shift + np.random.normal(0, 25)), 0)
    error_rate = np.clip(base_error_rate + scenario.error_shift + np.random.normal(0, 0.03), 0, 1)
    response = np.clip(
        base_response + (scenario.latency_shift * 3) + np.random.normal(0, 30), 1, 4000
    )

    return {
        "timestamp": pd.Timestamp.utcnow().isoformat(),
        "service_name": random.choice(["checkout", "auth", "payments", "catalog", "api-gateway"]),
        "cpu_usage": round(float(cpu), 2),
        "memory_usage": round(float(memory), 2),
        "disk_usage": round(float(disk), 2),
        "network_latency_ms": round(float(latency), 2),
        "request_count": int(requests),
        "error_rate": round(float(error_rate), 4),
        "response_time_ms": round(float(response), 2),
        "incident_label": scenario.label,
        "scenario_name": scenario.name,
    }


def generate_dataset(rows: int = 5000) -> pd.DataFrame:
    data = [generate_metric_row(i) for i in range(rows)]
    frame = pd.DataFrame(data)
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    frame["incident_label"] = frame["incident_label"].astype(int)
    return frame


def save_raw_dataset(path: Path | None = None, rows: int = 5000) -> Path:
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = path or (DATA_RAW_DIR / "synthetic_metrics.csv")
    generate_dataset(rows).to_csv(output_path, index=False)
    return output_path
