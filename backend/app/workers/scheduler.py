"""APScheduler lifecycle manager.

Exposes ``start_scheduler()`` and ``stop_scheduler()`` to be called from
FastAPI's startup/shutdown events.

Jobs
----
metric_ingestion   — every INGEST_INTERVAL_SECONDS (default 10 s)
alert_evaluator    — every INGEST_INTERVAL_SECONDS + 2 s (runs after ingestion)
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.workers.alert_evaluator import alert_evaluator_job
from backend.app.workers.metric_ingestion import INGEST_INTERVAL_SECONDS, ingest_metric_job

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    """Create and start the background scheduler with all registered jobs."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        logger.warning("Scheduler already running — skipping start")
        return

    _scheduler = BackgroundScheduler(
        job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 30}
    )

    _scheduler.add_job(
        ingest_metric_job,
        trigger=IntervalTrigger(seconds=INGEST_INTERVAL_SECONDS),
        id="metric_ingestion",
        name="Metric Ingestion",
        replace_existing=True,
    )

    _scheduler.add_job(
        alert_evaluator_job,
        trigger=IntervalTrigger(seconds=INGEST_INTERVAL_SECONDS + 2),
        id="alert_evaluator",
        name="Alert Evaluator",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info(
        "Background scheduler started — ingestion every %ds, alert eval every %ds",
        INGEST_INTERVAL_SECONDS,
        INGEST_INTERVAL_SECONDS + 2,
    )


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler on app shutdown."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")
    _scheduler = None


def get_scheduler_status() -> dict[str, object]:
    """Return scheduler state for the health/status endpoint."""
    if _scheduler is None or not _scheduler.running:
        return {"running": False, "jobs": []}
    return {
        "running": True,
        "jobs": [
            {"id": job.id, "name": job.name, "next_run": str(job.next_run_time)}
            for job in _scheduler.get_jobs()
        ],
    }
