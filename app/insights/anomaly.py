from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from app.models.observation import Observation
from app.insights.helpers import get_metric_series
import math

def compute_anomaly(db, source, metric, days=30) -> dict:
    series = dict(get_metric_series(db, source, metric, days))
    value =
    mean = 
    stddev = 
    z-score = abs(value - mean) > 2 * stddev
    return {}



def sync_correlations(db: Session) -> None:

    today = date.today()
