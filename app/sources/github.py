from datetime import datetime, timedelta, timezone
import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.observation import Observation

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!){
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
        contributionCalendar {
            weeks{
                contributionDays {
                    date
                    contributionCount
                    }
                }
            }
        }
    }
}
"""

def fetch_contributions(days: int = 30) -> list[dict]:
    now = datetime.now(timezone.utc)
    variables = {
        'login': settings.github_username,
        'from': (now - timedelta(days=days)).isoformat(),
        'to': now.isoformat()
    }
    response = httpx.post(
        GITHUB_GRAPHQL_URL,
        json={'query': QUERY, 'variables': variables},
        headers={'Authorization': f'Bearer {settings.github_token}'},
        timeout=10
    )
    response.raise_for_status()
    if 'errors' in response.json():
        raise Exception(f"GitHub API error: {response.json()['errors']}")
    data = response.json()['data']['user']['contributionsCollection']['contributionCalendar']
    days_out = []
    for week in data['weeks']:
        days_out.extend(week['contributionDays'])
    body = response.json()
    return days_out

def sync_github_activity(db: Session) -> None:
    for day in fetch_contributions():
        local_date = datetime.strptime(day['date'], "%Y-%m-%d").date()
        external_id = day['date']
        existing = db.query(Observation).filter_by(source='github', metric='contributions', external_id=external_id).one_or_none()
        if existing:
            existing.value_num = day['contributionCount']

        else:
            db.add(Observation(
                source='github',
                metric='contributions',
                timestamp=datetime.now(timezone.utc),
                local_date=local_date,
                value_num=day['contributionCount'],
                unit='contributions',
                external_id=external_id,
            ))

    db.commit()