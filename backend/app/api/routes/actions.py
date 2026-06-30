from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.action import ActionRead
from backend.app.services.incident_service import list_actions

router = APIRouter()


@router.get("", response_model=list[ActionRead])
def get_actions(
    db: Session = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)
) -> list[ActionRead]:
    return list_actions(db, limit=limit)
