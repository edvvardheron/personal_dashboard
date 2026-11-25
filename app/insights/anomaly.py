from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from app.models.observation import Observation
from app.insights.helpers import get_metric_series
from statistics import mean, stdev

def compute_anomaly(db, source, metric, days=30) -> dict | None:
    series = get_metric_series(db, source, metric, days)
    if len(series) < 7:
        return None
    *history, (latest_date, value) = series
    baseline = [v for _, v in history]
    average = mean(baseline)
    spread = stdev(baseline)
    if spread == 0:
        return None
    z_score = (value - average) / spread
    return {'z_score': z_score, 'is_anomaly': abs(z_score) > 2, 'mean': average, 'stddev': spread, 'date': latest_date, 'n': len(baseline)}



def sync_anomalies(db: Session) -> None:
    sources = [
        ('mood', 'score'),
        ('wakatime', 'coding_time'),
        ('github', 'contributions')
               ]

    today = date.today()
    for source, metric in sources:
        result = compute_anomaly(db, source, metric)
        if result is None:
            continue
        external_id = f'{source}.{metric}: {result["date"].date().isoformat()}'

        existing = db.query(Observation).filter_by(source='insights', metric='anomaly', external_id=external_id).one_or_none()

        if existing:
            existing.value_num = result['z_score']
            existing.meta = {'n': result['n'], 'mean': result['mean'], 'is_anomaly':result['is_anomaly']}
        else:
            db.add(Observation(
                source='insights',
                metric='anomaly',
                timestamp=datetime.now(timezone.utc),
                local_date=result['date'],
                value_num=result['z_score'],
                unit= 'z_score',
                meta= {'n': result['n'], 'mean': result['mean'], 'is_anomaly':result['is_anomaly'], 'stddev': result['stddev']},
                external_id=external_id

            ))
    db.commit()