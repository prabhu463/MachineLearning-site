"""Alert evaluator background worker.

Runs after every metric ingestion cycle. Loads all active Alert rules from
the DB, evaluates the most recently ingested metric against each rule, and
fires an alert event to the SSE bus when a threshold is breached.

In Phase 5 this will also create Incident rows and trigger notifications.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from backend.app.db.session import SessionLocal
from backend.app.models.alert import Alert
from backend.app.models.metric import Metric
from backend.app.workers.event_bus import event_bus

logger = logging.getLogger(__name__)

# Map operator strings to Python comparison lambdas
_OPERATORS: dict[str, Any] = {
    "gt":  lambda val, threshold: val >  threshold,
    "gte": lambda val, threshold: val >= threshold,
    "lt":  lambda val, threshold: val <  threshold,
    "lte": lambda val, threshold: val <= threshold,
}


def _evaluate_rule(rule: Alert, metric: Metric) -> bool:
    """Return True if *metric* breaches *rule*."""
    field_value = getattr(metric, rule.metric_field, None)
    if field_value is None:
        return False
    comparator = _OPERATORS.get(rule.operator)
    if comparator is None:
        logger.warning("Unknown alert operator '%s' on rule id=%d", rule.operator, rule.id)
        return False
    return bool(comparator(float(field_value), rule.threshold_value))


def alert_evaluator_job() -> None:
    """APScheduler job — evaluates the latest metric against all active alert rules."""
    db = SessionLocal()
    try:
        from sqlalchemy import select

        # Fetch latest metric
        latest: Metric | None = db.execute(
            select(Metric).order_by(Metric.created_at.desc()).limit(1)
        ).scalar_one_or_none()
        if latest is None:
            return

        # Fetch all active rules
        rules: list[Alert] = list(
            db.execute(select(Alert).where(Alert.is_active.is_(True))).scalars().all()
        )

        fired: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc)

        for rule in rules:
            if _evaluate_rule(rule, latest):
                logger.info(
                    "Alert fired: rule='%s' field=%s value=%s %s threshold=%s",
                    rule.name, rule.metric_field,
                    getattr(latest, rule.metric_field),
                    rule.operator, rule.threshold_value,
                )
                # Update last_fired_at
                rule.last_fired_at = now
                fired.append({
                    "alert_id": rule.id,
                    "alert_name": rule.name,
                    "metric_field": rule.metric_field,
                    "operator": rule.operator,
                    "threshold_value": rule.threshold_value,
                    "actual_value": getattr(latest, rule.metric_field),
                    "severity": rule.severity,
                    "service_name": latest.service_name,
                    "metric_id": latest.id,
                    "fired_at": now.isoformat(),
                })

        if fired:
            db.commit()
            # Publish all fired alerts to SSE bus
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    for alert_payload in fired:
                        loop.call_soon_threadsafe(
                            lambda p=alert_payload: asyncio.ensure_future(
                                event_bus.publish("alert", p)
                            )
                        )
            except RuntimeError:
                pass  # No event loop in test context

    except Exception as exc:  # noqa: BLE001
        logger.exception("Alert evaluator job failed: %s", exc)
    finally:
        db.close()
