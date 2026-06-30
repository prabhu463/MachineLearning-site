from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from backend.app.core.config import get_settings
from ml.src.constants import FEATURE_COLUMNS, MODELS_DIR, REPORTS_DIR
from ml.src.preprocessing import clean_data, engineer_features, impute_missing_values


@dataclass
class ModelArtifact:
    name: str
    version: str
    path: Path
    metrics: dict[str, float]


def load_dataset(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    return frame


def prepare_dataset(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    frame = load_dataset(path)
    frame = clean_data(frame)
    frame = engineer_features(frame)
    frame = impute_missing_values(frame)
    X = frame[FEATURE_COLUMNS]
    y = frame["incident_label"]
    return X, y


def evaluate_model(model, X_test, y_test) -> dict[str, float]:
    predictions = model.predict(X_test)
    proba = model.predict_proba(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, average="macro", zero_division=0)),
        "recall": float(recall_score(y_test, predictions, average="macro", zero_division=0)),
        "f1": float(f1_score(y_test, predictions, average="macro", zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba, multi_class="ovr")),
    }


def build_models(random_state: int = 42) -> dict[str, object]:
    return {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(max_iter=2000, multi_class="auto", random_state=random_state),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(random_state=random_state, n_estimators=250),
        "xgboost": XGBClassifier(
            random_state=random_state,
            n_estimators=220,
            learning_rate=0.08,
            max_depth=5,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="mlogloss",
            objective="multi:softprob",
            num_class=3,
        ),
    }


def tune_model(name: str, model, X_train, y_train):
    """Tune hyperparameters; returns (best_estimator, best_params).

    Notes
    -----
    LogisticRegression is wrapped in a Pipeline so its params are prefixed with
    ``model__``.  RandomForest and XGBoost are **not** Pipelines, so their param
    keys are flat (no prefix).
    """
    if name == "logistic_regression":
        # Pipeline step name is "model", so params use the "model__" prefix
        grid = {"model__C": [0.1, 1.0, 3.0]}
    elif name == "random_forest":
        grid = {"n_estimators": [150, 250], "max_depth": [None, 8, 14]}
    else:  # xgboost — flat keys, no Pipeline wrapper
        grid = {"n_estimators": [180, 260], "max_depth": [4, 6], "learning_rate": [0.05, 0.08]}
    try:
        search = GridSearchCV(model, grid, scoring="f1_macro", cv=3, n_jobs=-1)
        search.fit(X_train, y_train)
        return search.best_estimator_, search.best_params_
    except Exception as exc:  # noqa: BLE001
        import logging
        logging.getLogger(__name__).warning("GridSearchCV failed for %s: %s — using default params", name, exc)
        model.fit(X_train, y_train)
        return model, {}


def train_models(dataset_path: Path, random_state: int = 42) -> ModelArtifact:
    settings = get_settings()
    settings.ensure_dirs()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = prepare_dataset(dataset_path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=random_state
    )
    models = build_models(random_state=random_state)

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    best_result: tuple[str, object, dict[str, float], dict[str, object]] | None = None
    evaluation_rows: list[dict[str, object]] = []

    for name, model in models.items():
        with mlflow.start_run(run_name=name):
            tuned_model, best_params = tune_model(name, model, X_train, y_train)
            metrics = evaluate_model(tuned_model, X_test, y_test)
            evaluation_rows.append(
                {
                    "model": name,
                    **metrics,
                    "best_params": json.dumps(best_params),
                }
            )
            mlflow.log_params(best_params)
            mlflow.log_metrics(metrics)
            score = metrics["f1"] + metrics["roc_auc"]
            if best_result is None or score > (best_result[2]["f1"] + best_result[2]["roc_auc"]):
                best_result = (name, tuned_model, metrics, best_params)

    assert best_result is not None
    best_name, best_model, best_metrics, best_params = best_result
    artifact_path = MODELS_DIR / f"{best_name}_model.joblib"
    joblib.dump(
        {
            "model": best_model,
            "feature_columns": FEATURE_COLUMNS,
            "label_map": {0: "normal", 1: "warning", 2: "critical"},
            "metrics": best_metrics,
            "model_name": best_name,
        },
        artifact_path,
    )
    pd.DataFrame(evaluation_rows).to_csv(REPORTS_DIR / "model_comparison.csv", index=False)
    (REPORTS_DIR / "best_model.json").write_text(
        json.dumps(
            {
                "model_name": best_name,
                "artifact_path": str(artifact_path),
                "best_params": best_params,
                "metrics": best_metrics,
            },
            indent=2,
        )
    )
    return ModelArtifact(name=best_name, version="1.0.0", path=artifact_path, metrics=best_metrics)
