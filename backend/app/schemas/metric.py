from datetime import datetime

from pydantic import BaseModel, Field


class MetricBase(BaseModel):
    service_name: str = Field(min_length=1, max_length=120)
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    disk_usage: float = Field(ge=0, le=100)
    network_latency_ms: float = Field(ge=0)
    request_count: int = Field(ge=0)
    error_rate: float = Field(ge=0, le=1)
    response_time_ms: float = Field(ge=0)


class MetricCreate(MetricBase):
    pass


class MetricRead(MetricBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
