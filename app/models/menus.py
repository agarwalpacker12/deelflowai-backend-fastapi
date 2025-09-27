from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class Menus(Base):
    __tablename__ = "deelflow_menus"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    route: Mapped[str] = mapped_column(String(255), nullable=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_add: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_view: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_download: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # parent = relationship("Menus", remote_side=[id], backref="children")
    user_permissions = relationship(
        "UserMenuPermissions", back_populates="menu", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert the Menus model instance to a dictionary with optional children."""
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "name": self.name,
            "route": self.route,
            "icon": self.icon,
            "sort_order": self.sort_order,
            "is_active": self.is_active,
            "can_add": self.can_add,
            "can_edit": self.can_edit,
            "can_delete": self.can_delete,
            "can_view": self.can_view,
            "can_download": self.can_download,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }