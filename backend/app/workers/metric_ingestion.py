"""Metric ingestion background worker.

Every INGEST_INTERVAL_SECONDS the worker calls the synthetic data generator
to produce a single realistic metric row and persists it to the database.
This replaces the old manual-simulation-only data entry path.

The worker also publishes the new row to an in-process event bus so that
any connected SSE clients receive it instantly.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from backend.app.db.session import SessionLocal
from backend.app.models.metric import Metric
from backend.app.workers.event_bus import event_bus

logger = logging.getLogger(__name__)

# How often to generate and store a new metric (seconds)
INGEST_INTERVAL_SECONDS: int = 10


def _generate_one_metric() -> dict[str, Any]:
    """Call the ML data generator and return a single metric dict."""
    from ml.src.data_generation import generate_metric_row
    row = generate_metric_row(0)
    # Strip training-only keys not present in the DB schema
    return {
        "service_name": row["service_name"],
        "cpu_usage": row["cpu_usage"],
        "memory_usage": row["memory_usage"],
        "disk_usage": row["disk_usage"],
        "network_latency_ms": row["network_latency_ms"],
        "request_count": row["request_count"],
        "error_rate": row["error_rate"],
        "response_time_ms": row["response_time_ms"],
    }


def ingest_metric_job() -> None:
    """APScheduler job — runs in the scheduler thread pool."""
    try:
        data = _generate_one_metric()
        db = SessionLocal()
        try:
            metric = Metric(**data)
            db.add(metric)
            db.commit()
            db.refresh(metric)
            metric_id = metric.id
            created_at = metric.created_at.isoformat() if metric.created_at else datetime.now(timezone.utc).isoformat()
            logger.debug("Ingested metric id=%d service=%s cpu=%.1f%%", metric_id, data["service_name"], data["cpu_usage"])
        finally:
            db.close()

        # Publish to SSE event bus (non-blocking — schedule as coroutine)
        payload = {**data, "id": metric_id, "created_at": created_at}
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(
                    lambda: asyncio.ensure_future(event_bus.publish("metric", payload))
                )
        except RuntimeError:
            pass  # No event loop in test context — safe to skip

    except Exception as exc:  # noqa: BLE001
        logger.exception("Metric ingestion job failed: %s", exc)
