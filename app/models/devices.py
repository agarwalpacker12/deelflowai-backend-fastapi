from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, BIGINT, Text, event, DECIMAL, JSON, Time, CheckConstraint, Date, TEXT
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
from typing import Optional
from typing import Any

class Device(Base):
    __tablename__ = 'deelflow_devices'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('deelflow_user.id', ondelete='CASCADE'), nullable=False)
    device_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    device_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_os: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    location_json: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    last_login_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)


    def to_dict(self):
        """Convert the Device model instance to a dictionary."""
        return {
            "device_name": self.device_name,
            "device_ip": self.device_ip,
            "device_ip": self.device_ip,
            "device_os": self.device_os,
            "location_json": self.location_json,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at,
        }

