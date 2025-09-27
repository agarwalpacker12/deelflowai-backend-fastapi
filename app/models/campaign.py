from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID

class Campaign(Base):
    __tablename__ = "deelflow_campaign"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    budget: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    campaign_type: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    distress_indicators: Mapped[str] = mapped_column(Text, nullable=False)
    email_content: Mapped[str] = mapped_column(Text, nullable=False)
    geographic_scope_type: Mapped[str] = mapped_column(Text, nullable=False)
    geographic_scope_values: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=False)
    max_price: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    min_price: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    minimum_equity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    property_type: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    subject_line: Mapped[str] = mapped_column(Text, nullable=False)
    use_ai_personalization: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def to_dict(self) -> dict:
        """
        Convert the Campaign model instance to a dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "budget": self.budget,
            "campaign_type": self.campaign_type,
            "channel": self.channel,
            "distress_indicators": self.distress_indicators,
            "email_content": self.email_content,
            "geographic_scope_type": self.geographic_scope_type,
            "geographic_scope_values": self.geographic_scope_values,
            "location": self.location,
            "max_price": self.max_price,
            "min_price": self.min_price,
            "minimum_equity": self.minimum_equity,
            "property_type": self.property_type,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "subject_line": self.subject_line,
            "use_ai_personalization": self.use_ai_personalization,
        }