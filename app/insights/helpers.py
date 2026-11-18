from datetime import datetime, timedelta, date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.observation import Observation

def get_metric_series(db: Session, source: str, metric: str, days: int = 30) -> list[tuple[date, float]]:
    """
    Get a time series of metric values for a given source and metric over the last `days` days.

    Args:
        db (Session): The database session.
        source (str): The source of the metric.
        metric (str): The name of the metric.
        days (int): The number of days to look back from today.

    Returns:
        list[tuple[date, float]]: A list of tuples containing the date and the corresponding metric value.
    """
    cutoff = date.today() - timedelta(days=days)
    rows = db.scalars(
        select(Observation).where
        (
            Observation.source == source,
            Observation.metric == metric,
            Observation.local_date >= cutoff
        )
        .order_by(Observation.local_date)
    ).all()

    return [(row.local_date, row.value_num) for row in rows if row.value_num is not None]