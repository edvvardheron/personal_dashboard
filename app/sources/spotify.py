from datetime import datetime, date, timezone
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.observation import Observation
import base64


def get_spotify_access_token() -> str:
    auth = base64.b64encode(f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()).decode()
    response = httpx.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth}"},
        data={
            "grant_type": "client_credentials",
            "refresh_token": settings.SPOTIFY_REFRESH_TOKEN
        },
    )
    response.raise_for_status()
    return response.json()['access_token']


def fetch_listening_time() -> float:
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"


def sync_spotify_activity(db: Session) -> None:
    today = date.today()
    external_id = today.isoformat()
    existing = db.query(Observation).filter_by(source='spotify', metric='listening_time', external_id=external_id).one_or_none()
    if existing:
        existing.value_num = fetch_listening_time()
    else:
        db.add(Observation(
            source='spotify',
            metric='listening_time',
            timestamp=datetime.now(timezone.utc),
            local_date=today,
            value_num=fetch_listening_time(),
            unit='time',
            external_id=external_id
        ))
    db.commit()