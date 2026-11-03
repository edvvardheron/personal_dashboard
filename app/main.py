from datetime import date, datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.observation import Observation
from app.core.config import settings

import secrets

app = FastAPI(title='personal dashboard', description='A personal dashboard for monitoring and managing various tasks.', version='1.0.0')
bearer = HTTPBearer(auto_error=False)



def require_api_key(creds=Depends(bearer)):
    if creds is None or not secrets.compare_digest(creds.credentials, settings.api_key):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get('/sources', dependencies=[Depends(require_api_key)])
def list_sources(db: Session = Depends(get_db)):
    return db.scalars(select(Observation.source).distinct()).all()

