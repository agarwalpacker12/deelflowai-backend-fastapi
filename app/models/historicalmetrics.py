from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class HistoricalMetrics(Base):
    __tablename__ = "deelflow_historicalmetrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    metric_type: Mapped[str] = mapped_column(Text, nullable=False)
    metric_value: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    record_date: Mapped[Date] = mapped_column(
        Date,
        server_default=func.current_date(),  # Default to today
        nullable=False
    )

    def to_dict(self) -> dict:
        """
        Convert the HistoricalMetrics model instance to a dictionary.
        """
        return {
            "id": self.id,
            "metric_type": self.metric_type,
            "metric_value": self.metric_value,
            "record_date": self.record_date.isoformat() if self.record_date else None
        }