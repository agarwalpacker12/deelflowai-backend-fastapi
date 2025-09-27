from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class Organization(Base):
    __tablename__ = "deelflow_organization"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    subscription_status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    #relationship
    user = relationship("User", back_populates="organization", uselist=False)
    
    def to_dict(self) -> dict:
        """
        Convert the User model instance to a dictionary, including related `role` data.
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "slug": self.slug,
            "subscription_status": self.subscription_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }