from datetime import date, timezone, datetime
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.observation import Observation
import base64



def fetch_coding_time() -> float:
    url = "https://wakatime.com/api/v1/users/current/statusbar/today"
    token = base64.b64encode(f"{settings.wakatime_api_key}:".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}"
    }
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    if 'errors' in data:
        raise Exception(f'WakaTime API error: {data["errors"]}')

    return data['data']['grand_total']['minutes'] 

def sync_wakatime_activity(db: Session) -> None:
    today = date.today()
    external_id = today.isoformat()
    existing = db.query(Observation).filter_by(source='wakatime', metric='coding_time', external_id=external_id).one_or_none()
    if existing:
        existing.value_num = fetch_coding_time()
    else:
        db.add(Observation(
            source='wakatime',
            metric='coding_time',
            timestamp=datetime.now(timezone.utc),
            local_date=today,
            value_num=fetch_coding_time(),
            unit='time',
            external_id=external_id
        ))
    db.commit()