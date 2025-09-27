from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class CampaignPerformance(Base):
    __tablename__ = "deelflow_campaignperformance"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    campaign_type: Mapped[str] = mapped_column(Text, nullable=False)
    roi_percentage: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
    date_range: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        """
        Convert the CampaignPerformance model instance to a dictionary.
        """
        return {
            "id": self.id,
            "campaign_type": self.campaign_type,
            "roi_percentage": self.roi_percentage,
            "date_range": self.date_range,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }