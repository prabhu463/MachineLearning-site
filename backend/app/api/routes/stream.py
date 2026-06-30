"""Server-Sent Events (SSE) streaming endpoint.

Clients connect to GET /api/v1/stream/{topic} and receive a continuous
stream of JSON events whenever the backend publishes to that topic.

Supported topics
----------------
metric   — new metric row ingested by the background worker
alert    — alert rule fired by the evaluator

The frontend live-monitoring page connects here to update charts in real
time without polling.
"""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from backend.app.workers.event_bus import event_bus

logger = logging.getLogger(__name__)
router = APIRouter()

_ALLOWED_TOPICS = {"metric", "alert"}


@router.get("/{topic}")
async def stream_topic(topic: str) -> EventSourceResponse:
    """Stream live events for *topic* as Server-Sent Events.

    The client must include ``Accept: text/event-stream`` in the request.
    Each event is a JSON-encoded payload matching the topic's schema.
    """
    if topic not in _ALLOWED_TOPICS:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown topic '{topic}'. Allowed: {sorted(_ALLOWED_TOPICS)}",
        )

    async def event_generator():
        queue = event_bus.subscribe(topic)
        logger.info("SSE client connected: topic=%s  subscribers=%d", topic, event_bus.subscriber_count(topic))
        try:
            # Send an initial heartbeat so the client knows the stream is live
            yield {"event": "connected", "data": json.dumps({"topic": topic, "status": "streaming"})}
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=25.0)
                    yield {"event": topic, "data": json.dumps(payload)}
                except asyncio.TimeoutError:
                    # Send a keep-alive comment every 25 s to prevent proxy timeouts
                    yield {"event": "heartbeat", "data": "{}"}
        except asyncio.CancelledError:
            pass
        finally:
            event_bus.unsubscribe(topic, queue)
            logger.info("SSE client disconnected: topic=%s  remaining=%d", topic, event_bus.subscriber_count(topic))

    return EventSourceResponse(event_generator())
