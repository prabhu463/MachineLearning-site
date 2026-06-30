from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    metric_field: str = Field(
        min_length=1, max_length=80,
        description="Metric column to watch: cpu_usage | memory_usage | disk_usage | error_rate | network_latency_ms | response_time_ms | request_count",
    )
    operator: str = Field(
        pattern="^(gt|gte|lt|lte)$",
        description="Comparison: gt | gte | lt | lte",
    )
    threshold_value: float = Field(description="Numeric threshold to compare against")
    severity: str = Field(default="warning", pattern="^(info|warning|critical)$")
    channel: str = Field(default="none", pattern="^(email|slack|webhook|none)$")
    channel_target: str = Field(default="", max_length=255)


class AlertRead(AlertCreate):
    id: int
    is_active: bool
    created_at: datetime
    last_fired_at: datetime | None = None

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    is_active: bool | None = None
    threshold_value: float | None = None
    severity: str | None = Field(default=None, pattern="^(info|warning|critical)$")
    channel: str | None = Field(default=None, pattern="^(email|slack|webhook|none)$")
    channel_target: str | None = None
