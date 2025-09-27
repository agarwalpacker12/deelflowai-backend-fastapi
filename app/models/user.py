from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "deelflow_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)

    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    role: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    points: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    stripe_customer_id: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    organization_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('deelflow_organization.id', ondelete='CASCADE'), nullable=False)

    password: Mapped[str] = mapped_column(Text, nullable=False)

    # Relatationship
    menu_permissions = relationship(
        "UserMenuPermissions", back_populates="user", cascade="all, delete-orphan"
    )
    organization = relationship("Organization", back_populates="user")
    
    
    def to_dict(self) -> dict:
        """
        Convert the User model instance to a dictionary, including related `role` data.
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "role": self.role,
            "level": self.level,
            "points": self.points,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "stripe_customer_id": self.stripe_customer_id,
            "created_at": self.created_at,
            "organization": self.organization.to_dict() if self.organization else None,
        }
    
    def to_dict_menu(self) -> dict:
        """
        Convert the User model instance to a dictionary, including related `role` data.
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "role": self.role,
            "level": self.level,
            "points": self.points,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "stripe_customer_id": self.stripe_customer_id,
            "created_at": self.created_at,
            "organization": self.organization.to_dict() if self.organization else None,
            "menu_permissions": [menu_permission.to_dict() for menu_permission in self.menu_permissions] if hasattr(self, "menu_permissions") else []
        }