from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.router import api_router
from backend.app.core.config import get_settings
from backend.app.core.exceptions import unhandled_exception_handler, value_error_handler
from backend.app.core.logging import configure_logging
from backend.app.core.middleware import RequestIDMiddleware
from backend.app.db.session import Base, engine
from backend.app.models import ActionEvent, Alert, Incident, Metric, ModelRegistry, User
from backend.app.workers.scheduler import get_scheduler_status, start_scheduler, stop_scheduler

configure_logging()
settings = get_settings()
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="PredictiveOps AI predicts incidents, explains root causes, and orchestrates remediation.",
)

# ── Middleware (outermost first) ──────────────────────────────────────────────
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": settings.app_name,
        "status": "running",
        "version": "1.0.0",
        "scheduler": get_scheduler_status(),
    }


@app.on_event("startup")
async def on_startup() -> None:
    logger.info(
        "PredictiveOps AI starting — env=%s  db=%s",
        settings.environment,
        settings.database_url.split("///")[-1],
    )
    start_scheduler()
    logger.info("Background workers started")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    stop_scheduler()
    logger.info("Background workers stopped — shutdown complete")
