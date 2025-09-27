from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class ComplianceStatus(Base):
    __tablename__ = "deelflow_compliancestatus"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    compliance_percent: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    audit_trail: Mapped[str] = mapped_column(Text, nullable=False)
    system_health: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict:
        """
        Convert the ComplianceStatus model instance to a dictionary.
        """
        return {
            "id": self.id,
            "compliance_percent": self.compliance_percent,
            "audit_trail": self.audit_trail,
            "system_health": self.system_health,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }