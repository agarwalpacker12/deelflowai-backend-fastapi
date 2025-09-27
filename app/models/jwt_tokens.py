from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, BIGINT, Text, event, DECIMAL, JSON, Time, CheckConstraint, Date, TEXT
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
from typing import Any

class JwtToken(Base):
    __tablename__ = 'deelflow_jwt_tokens'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('deelflow_user.id', ondelete='CASCADE'), nullable=False)
    device_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('deelflow_devices.id', ondelete='CASCADE'), nullable=False)
    access_jti: Mapped[str] = mapped_column(String(256), nullable=False)
    refresh_jti: Mapped[str] = mapped_column(String(256), nullable=False)
    device_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    expires_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, onupdate=func.now(), nullable=True)
    


