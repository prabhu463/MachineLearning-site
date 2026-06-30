"""Validation tests for Request-ID middleware."""

import uuid

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a unique request ID into every request context and response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def create_test_app():
    """Create a FastAPI app with middleware for testing."""
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/test")
    @app.post("/test")
    @app.put("/test")
    @app.delete("/test")
    async def test_endpoint(request: Request):
        return {"request_id": getattr(request.state, "request_id", None)}

    return app


def test_middleware_generates_request_id():
    """Test that middleware generates a UUID when no header present."""
    client = TestClient(create_test_app())
    response = client.get("/test")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert uuid.UUID(request_id) is not None


def test_middleware_preserves_existing_request_id():
    """Test that middleware preserves existing X-Request-ID header."""
    app = create_test_app()
    test_req_id = "test-req-12345"
    client = TestClient(app)
    response = client.get("/test", headers={"X-Request-ID": test_req_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == test_req_id


def test_middleware_request_id_in_context():
    """Test that request ID is available in request context."""
    client = TestClient(create_test_app())
    response = client.get("/test")

    assert response.status_code == 200
    request_id = response.json().get("request_id")
    assert request_id is not None
    assert response.headers["X-Request-ID"] == request_id


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
def test_middleware_works_across_http_methods(method):
    """Test middleware works correctly with all HTTP methods."""
    client = TestClient(create_test_app())
    response = client.request(method, "/test")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert uuid.UUID(response.headers["X-Request-ID"])


def test_middleware_unique_ids_per_request():
    """Test that each request gets a unique ID."""
    client = TestClient(create_test_app())
    response1 = client.get("/test")
    response2 = client.get("/test")

    assert response1.headers["X-Request-ID"] != response2.headers["X-Request-ID"]