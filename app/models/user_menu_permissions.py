from sqlalchemy import Column, String, BigInteger, ForeignKey, Enum, TIMESTAMP, DateTime, Boolean, Integer, func, Index, DECIMAL, Text, Date
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from sqlalchemy.orm import Mapped
from app.config.db_connection import Base
import pytz
from sqlalchemy.dialects.postgresql import UUID


class UserMenuPermissions(Base):
    __tablename__ = "deelflow_user_menu_permissions"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("deelflow_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    menu_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("deelflow_menus.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Permissions
    can_add: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_download: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
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
    # user = relationship("User", backref="menu_permissions")
    user = relationship("User", back_populates="menu_permissions")
    menu = relationship("Menus", back_populates="user_permissions")


    def to_dict(self) -> dict:
        """Convert the UserMenuPermissions instance to a dictionary."""
        return {
            "id": self.id,
            # "user_id": self.user_id,
            # "menu_id": self.menu_id,
            "menu": self.menu.to_dict() if self.menu else None,
            "can_add": self.can_add,
            "can_edit": self.can_edit,
            "can_delete": self.can_delete,
            "can_view": self.can_view,
            "can_download": self.can_download,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }