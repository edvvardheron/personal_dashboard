from datetime import date, datetime
from sqlalchemy import DateTime, Index, JSON, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class Observation(Base):
    __tablename__ = 'observations'
    __table_args__ = (
        UniqueConstraint('source', 'metric', 'external_id'),
                         Index('ix_obs_metric_ts', 'metric', 'timestamp'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str]
    metric: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    local_date: Mapped[date] = mapped_column(DateTime(timezone=True))
    value_num: Mapped[float | None]
    value_text: Mapped[str | None]
    unit: Mapped[str | None]
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    external_id: Mapped[str]
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

