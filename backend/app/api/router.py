from fastapi import APIRouter

from backend.app.api.routes import (
    actions,
    alerts,
    dashboard,
    health,
    incidents,
    metrics,
    models,
    predictions,
    stream,
)

api_router = APIRouter()
api_router.include_router(health.router,       tags=["health"])
api_router.include_router(metrics.router,      prefix="/metrics",    tags=["metrics"])
api_router.include_router(incidents.router,    prefix="/incidents",  tags=["incidents"])
api_router.include_router(actions.router,      prefix="/actions",    tags=["actions"])
api_router.include_router(predictions.router,  prefix="/predict",    tags=["predictions"])
api_router.include_router(dashboard.router,    prefix="/dashboard",  tags=["dashboard"])
api_router.include_router(models.router,       prefix="/models",     tags=["models"])
api_router.include_router(alerts.router,       prefix="/alerts",     tags=["alerts"])
api_router.include_router(stream.router,       prefix="/stream",     tags=["stream"])
