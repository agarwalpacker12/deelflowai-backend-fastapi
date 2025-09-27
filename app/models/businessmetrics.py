from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class BusinessMetrics(Base):
    __tablename__ = "deelflow_businessmetrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    total_revenue: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_users: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    properties_listed: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_deals: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    monthly_profit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    voice_calls_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    report_date: Mapped[Date] = mapped_column(
        Date, 
        server_default=func.current_date(),  # Default to today
        nullable=False
    )

    ai_conversations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def to_dict(self) -> dict:
        """
        Convert the BusinessMetrics model instance to a dictionary.
        """
        return {
            "id": self.id,
            "total_revenue": self.total_revenue,
            "active_users": self.active_users,
            "properties_listed": self.properties_listed,
            "total_deals": self.total_deals,
            "monthly_profit": self.monthly_profit,
            "voice_calls_count": self.voice_calls_count,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "ai_conversations": self.ai_conversations
        }