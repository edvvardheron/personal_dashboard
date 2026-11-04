from datetime import date, datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.observation import Observation

def make_obs():
    return Observation(
        source='GitHub',
        metric='commits',
        timestamp=datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc),
        local_date=date(2026, 11, 4),
        external_id='gh:2026-11-04:commits'
    )

def test_deplicate_observation_is_rejected(db):
    db.add(make_obs())
    db.commit()
    db.add(make_obs())
    with pytest.raises(IntegrityError):
        db.commit()

def test_sources_lists_distinct_sources(client, db):
    db.add(make_obs())
    db.commit()
    headers = {'Authorization': f'Bearer {settings.api_key}'}
    r = client.get('/sources', headers=headers)
    assert r.status_code == 200
    assert r.json() == ['GitHub']


def test_sources_requires_api_key(client):
    assert client.get('/sources').status_code == 403

def test_sources_rejects_invalid_api_key(client):
    headers = {'Authorization': 'Bearer invalid_key'}
    assert client.get('/sources', headers=headers).status_code == 403