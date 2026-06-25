from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def build_actions(recommendation: str, severity: str) -> list[str]:
    mapping = {
        "restart": "Restart service",
        "scale": "Scale application",
        "rollback": "Rollback deployment",
        "cache": "Clear cache",
        "increase": "Increase resources",
        "memory leak": "Restart service",
    }
    lowered = recommendation.lower()
    actions = []
    for key, title in mapping.items():
        if key in lowered and title not in actions:
            actions.append(title)
    if not actions:
        actions = ["Investigate logs", "Notify on-call engineer"]
    if severity == "critical":
        actions.insert(0, "Page incident response")
    return actions


def execute_action(action_name: str, incident_id: int, mode: str = "simulate") -> dict[str, str]:
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info("Executing remediation action %s for incident %s in mode=%s", action_name, incident_id, mode)
    if mode == "simulate":
        status = "simulated"
        details = f"{action_name} scheduled at {timestamp}"
    else:
        status = "executed"
        details = f"{action_name} executed at {timestamp}"
    return {"status": status, "details": details}
