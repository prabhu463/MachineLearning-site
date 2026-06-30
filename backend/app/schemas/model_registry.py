from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ModelRegistryRead(BaseModel):
    """Pydantic schema for reading a ModelRegistry row."""

    id: int
    model_name: str
    model_version: str
    artifact_path: str
    metrics_json: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class TrainRequest(BaseModel):
    """Optional parameters a caller may supply to the training endpoint."""

    rows: int = Field(default=5000, ge=500, le=50_000, description="Synthetic dataset rows to generate")
    random_state: int = Field(default=42, ge=0)


class TrainResponse(BaseModel):
    """Result returned after a successful training run."""

    model_name: str
    version: str
    artifact_path: str
    metrics: dict[str, float]
    registry_id: int

    model_config = {"protected_namespaces": ()}


class ModelInfoResponse(BaseModel):
    """Lightweight model-info response (no DB lookup required)."""

    model_name: str
    artifact_path: str
    is_loaded: bool
    metrics: dict[str, float]
    feature_columns: list[str]

    model_config = {"protected_namespaces": ()}
