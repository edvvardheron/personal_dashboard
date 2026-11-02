from datetime import date, datetime

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import require_api_key
from app.core.db import get_db
from app.models.observation import Observation

app = FastAPI(title='personal dashboard', description='A personal dashboard for monitoring and managing various tasks.', version='1.0.0')

class ObservationIn(BaseModel):
    source: str
    metric: str
    timestamp: datetime
    local_date: date
    value_num: float | None = None
    value_text: str | None = None
    unit: str | None = None
    meta: dict = {}
    external_id: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/metrics", dependencies=[Depends(require_api_key)])
def metrics():
    return {"metrics": "some metrics data"}

@app.get('/sources', dependencies=[Depends(require_api_key)])
def list_sources(db: Session = Depends(get_db)):
    return db.scalars(select(Observation.source).distinct()).all()

@app.post('/observations', dependencies=[Depends(require_api_key)])
def create_observation(observation: ObservationIn, db: Session = Depends(get_db)):
    row = Observation(**observation.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row