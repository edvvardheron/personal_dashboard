from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db, SessionLocal
from app.models.observation import Observation
from app.core.config import settings
from app.core.auth import require_api_key

from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.sources.github import sync_github_activity, fetch_contributions

'''
GET = for retrieving data from the server. It is used to request data from a specified resource.
POST = for sending data to the server. It is used to submit data to be processed to a specified resource.
DELETE = for deleting data from the server. It is used to delete a specified resource.
PUT = for updating data on the server. It is used to update a specified resource with new data.
'''

def run_github_sync():
    with SessionLocal() as db:
        sync_github_activity(db)

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_github_sync() # Run the sync immediately on startup
    scheduler.add_job(run_github_sync, 'interval', hours=12)  # schedule to run every 12 hours
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title='personal dashboard', lifespan=lifespan)

bearer = HTTPBearer(auto_error=False)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get('/sources', dependencies=[Depends(require_api_key)])
def list_sources(db: Session = Depends(get_db)):
    return db.scalars(select(Observation.source).distinct()).all()

@app.get('/observations', dependencies=[Depends(require_api_key)])
def list_observations(source: str | None = None, db: Session = Depends(get_db)):
    query = select(Observation)
    if source:
        query = query.where(Observation.source == source)
    return db.scalars(query).all()

