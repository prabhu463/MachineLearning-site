"""Lightweight in-process async event bus for SSE broadcasting.

Any worker thread can call ``event_bus.publish(topic, payload)`` and all
SSE clients subscribed to that topic receive the event instantly — no
Redis or external broker required for a single-process deployment.
"""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)


class EventBus:
    """Async pub/sub hub backed by asyncio.Queue per subscriber."""

    def __init__(self) -> None:
        # topic → list of asyncio.Queue
        self._subscribers: dict[str, list[asyncio.Queue[Any]]] = defaultdict(list)

    def subscribe(self, topic: str) -> asyncio.Queue[Any]:
        """Return a queue that will receive events published to *topic*."""
        q: asyncio.Queue[Any] = asyncio.Queue(maxsize=100)
        self._subscribers[topic].append(q)
        logger.debug("SSE subscriber added for topic=%s  total=%d", topic, len(self._subscribers[topic]))
        return q

    def unsubscribe(self, topic: str, queue: asyncio.Queue[Any]) -> None:
        """Remove a subscriber queue (called when the client disconnects)."""
        try:
            self._subscribers[topic].remove(queue)
            logger.debug("SSE subscriber removed for topic=%s  remaining=%d", topic, len(self._subscribers[topic]))
        except ValueError:
            pass

    async def publish(self, topic: str, payload: Any) -> None:
        """Broadcast *payload* to all subscribers of *topic*."""
        dead: list[asyncio.Queue[Any]] = []
        for q in list(self._subscribers.get(topic, [])):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                # Slow consumer — drop the event rather than block
                logger.warning("SSE queue full for topic=%s — dropping event", topic)
            except Exception as exc:  # noqa: BLE001
                logger.warning("SSE publish error: %s", exc)
                dead.append(q)
        for q in dead:
            self.unsubscribe(topic, q)

    def subscriber_count(self, topic: str) -> int:
        return len(self._subscribers.get(topic, []))


# Module-level singleton — shared across the whole process
event_bus = EventBus()
