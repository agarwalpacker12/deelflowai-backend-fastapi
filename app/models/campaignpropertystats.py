from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class CampaignPropertyStats(Base):
    __tablename__ = "deelflow_campaignpropertystats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    total_properties: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
    distressed_properties: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
    competition_level: Mapped[str] = mapped_column(Text, nullable=False)
    avg_roi: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default="0"
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        """
        Convert the CampaignPropertyStats model instance to a dictionary.
        """
        return {
            "id": self.id,
            "total_properties": self.total_properties,
            "distressed_properties": self.distressed_properties,
            "competition_level": self.competition_level,
            "avg_roi": self.avg_roi,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }