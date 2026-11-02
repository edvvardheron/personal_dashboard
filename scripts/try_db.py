from datetime import datetime, date, timezone
from sqlalchemy import select
from app.core.db import Base, SessionLocal, engine
from app.models.observation import Observation

# Base.metadata.create_all(bind=engine) #temporary, Alembic will handle this in the future

with SessionLocal() as db:
    db.add(Observation(
        source='test_source',
        metric='test_metric',
        timestamp=datetime.now(timezone.utc),
        local_date=date.today(),
        value_num=42.0,
        value_text='test_value',
        unit='test_unit',
        meta={'key': 'value'},
        external_id='test_external_id'
    ))
    db.commit()

    rows = db.scalars(select(Observation).where(Observation.metric == 'test_metric')).all()
    print(rows[0].value_num)  # Output: 42.0