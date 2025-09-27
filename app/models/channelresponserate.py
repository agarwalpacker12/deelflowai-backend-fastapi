from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class ChannelResponseRate(Base):
    __tablename__ = "deelflow_channelresponserate"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    channel_name: Mapped[str] = mapped_column(Text, nullable=False)
    response_rate: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
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
        Convert the ChannelResponseRate model instance to a dictionary.
        """
        return {
            "id": self.id,
            "channel_name": self.channel_name,
            "response_rate": self.response_rate,
            "date_range": self.date_range,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }