from datetime import datetime, timezone, date
from scipy.stats import pearsonr
from sqlalchemy.orm import Session
from app.models.observation import Observation
from app.insights.helpers import get_metric_series
import math

def compute_correlation(db, source_a, metric_a, source_b, metric_b, days=30) -> dict:
    series_a = dict(get_metric_series(db, source_a, metric_a, days))
    series_b = dict(get_metric_series(db, source_b, metric_b, days))
    common_dates = sorted(set(series_a) & set(series_b))
    if len(common_dates) < 5:
        return None # not enough overlap to mean anything
    values_a = [series_a[d] for d in common_dates]
    values_b = [series_b[d] for d in common_dates]
    coefficient, p_value, = pearsonr(values_a, values_b)
    if math.isnan(coefficient):
        return None
    return {'coefficient': coefficient, 'p_value': p_value, 'n': len(common_dates)}


def sync_correlations(db: Session) -> None:
    pairs = [
        ('mood', 'score', 'wakatime', 'coding_time'),
        ('mood', 'score', 'github', 'contributions'),
        ('wakatime', 'coding_time', 'github', 'contributions')
    ]
    today = date.today()
    for source_a, metric_a, source_b, metric_b in pairs:
        result = compute_correlation(db, source_a, metric_a, source_b, metric_b)
        if result is None:
            continue
        external_id = f'{source_a}.{metric_a}_x_{source_b}.{metric_b}: {today.isoformat()}'
        existing = db.query(Observation).filter_by(source='insights', metric='correlation', external_id = external_id).one_or_none()

        if existing:
            existing.value_num = result['coefficient']
        else:
            db.add(Observation(
                source='insights',
                metric='correlation',
                timestamp=datetime.now(timezone.utc),
                local_date=today,
                value_num=result['coefficient'],
                unit='pearson_r',
                meta={'p_value': result['p_value'], 'n': result['n']},
                external_id=external_id
            ))
    db.commit()
