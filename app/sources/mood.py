from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone

from app.core.auth import require_api_key
from app.core.db import get_db
from app.models.observation import Observation
from fastapi import APIRouter, Depends

router = APIRouter()

class Mood(BaseModel):
    score: int = Field(ge=1, le=5)
@router.put("/mood", dependencies=[Depends(require_api_key)])
def update_mood(mood: Mood, db: Session = Depends(get_db)):
    today = date.today()
    external_id = today.isoformat()
    existing = db.query(Observation).filter_by(source='mood', metric='score', external_id=external_id).one_or_none()
    if existing:
        existing.value_num = mood.score
    else:
        db.add(Observation(
            source='mood',
            metric='score',
            timestamp=datetime.now(timezone.utc),
            local_date=today,
            value_num=mood.score,
            unit='score',
            external_id=external_id
        ))
    db.commit()