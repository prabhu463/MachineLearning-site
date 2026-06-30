from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_DIR = PROJECT_ROOT / "ml"
DATA_RAW_DIR = ML_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ML_DIR / "data" / "processed"
MODELS_DIR = ML_DIR / "models"
REPORTS_DIR = ML_DIR / "reports"

FEATURE_COLUMNS = [
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "network_latency_ms",
    "request_count",
    "error_rate",
    "response_time_ms",
    "rolling_cpu_mean",
    "rolling_memory_mean",
    "rolling_error_mean",
    "latency_to_response_ratio",
]

LABEL_MAP = {0: "normal", 1: "warning", 2: "critical"}
