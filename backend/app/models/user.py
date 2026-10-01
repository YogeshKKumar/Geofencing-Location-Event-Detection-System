from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="USER", nullable=False)  # "ADMIN", "USER"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    devices: Mapped[List["Device"]] = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    created_geofences: Mapped[List["Geofence"]] = relationship("Geofence", back_populates="creator")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
    location_events: Mapped[List["LocationEvent"]] = relationship("LocationEvent", back_populates="user")
    geofence_events: Mapped[List["GeofenceEvent"]] = relationship("GeofenceEvent", back_populates="user")
