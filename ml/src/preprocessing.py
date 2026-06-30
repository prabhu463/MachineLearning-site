from __future__ import annotations

import pandas as pd
from sklearn.impute import SimpleImputer


def clean_data(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    cleaned = cleaned.drop_duplicates()
    numeric_cols = cleaned.select_dtypes(include=["number"]).columns
    cleaned[numeric_cols] = cleaned[numeric_cols].clip(lower=0)
    return cleaned


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    engineered = frame.copy()
    engineered = engineered.sort_values("timestamp").reset_index(drop=True)
    engineered["rolling_cpu_mean"] = engineered["cpu_usage"].rolling(window=5, min_periods=1).mean()
    engineered["rolling_memory_mean"] = (
        engineered["memory_usage"].rolling(window=5, min_periods=1).mean()
    )
    engineered["rolling_error_mean"] = engineered["error_rate"].rolling(window=5, min_periods=1).mean()
    engineered["latency_to_response_ratio"] = engineered["network_latency_ms"] / (
        engineered["response_time_ms"] + 1e-6
    )
    return engineered


def impute_missing_values(frame: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = frame.select_dtypes(include=["number"]).columns
    imputer = SimpleImputer(strategy="median")
    frame[numeric_cols] = imputer.fit_transform(frame[numeric_cols])
    return frame
