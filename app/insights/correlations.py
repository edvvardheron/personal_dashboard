from datetime import datetime, timedelta, date
from scipy.stats import pearsonr
from sqlalchemy.orm import Session
from app.models.observation import Observation
from app.insights.helpers import get_metric_series 