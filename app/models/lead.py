from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class Lead(Base):
    __tablename__ = "deelflow_lead"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    responded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    campaign_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('deelflow_campaign.id', ondelete='CASCADE'), nullable=False
    )

    def to_dict(self) -> dict:
        """
        Convert the Lead model instance to a dictionary.
        """
        return {
            "id": self.id,
            "status": self.status,
            "responded": self.responded,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "campaign_id": self.campaign_id,
        }