"""Unit tests for the global exception handlers."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.core.exceptions import unhandled_exception_handler, value_error_handler


def _make_request(path: str = "/test") -> MagicMock:
    req = MagicMock()
    req.method = "GET"
    req.url.path = path
    return req


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500():
    request = _make_request("/api/v1/predict")
    exc = RuntimeError("something exploded")
    response = await unhandled_exception_handler(request, exc)
    assert response.status_code == 500
    import json
    body = json.loads(response.body)
    assert body["error"] == "internal_server_error"
    assert body["path"] == "/api/v1/predict"


@pytest.mark.asyncio
async def test_value_error_returns_422():
    request = _make_request("/api/v1/metrics")
    exc = ValueError("invalid metric value")
    response = await value_error_handler(request, exc)
    assert response.status_code == 422
    import json
    body = json.loads(response.body)
    assert body["error"] == "validation_error"
    assert "invalid metric value" in body["message"]
