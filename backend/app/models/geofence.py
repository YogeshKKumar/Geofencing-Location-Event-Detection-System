from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Geofence(Base):
    __tablename__ = "geofences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # "CIRCLE" or "POLYGON"
    center_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    center_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    radius_meters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    creator: Mapped[Optional["User"]] = relationship("User", back_populates="created_geofences")
    points: Mapped[List["GeofencePoint"]] = relationship(
        "GeofencePoint",
        back_populates="geofence",
        cascade="all, delete-orphan",
        order_by="GeofencePoint.point_order"
    )
    geofence_events: Mapped[List["GeofenceEvent"]] = relationship(
        "GeofenceEvent",
        back_populates="geofence",
        cascade="all, delete-orphan"
    )


class GeofencePoint(Base):
    __tablename__ = "geofence_points"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    geofence_id: Mapped[int] = mapped_column(ForeignKey("geofences.id", ondelete="CASCADE"), index=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    point_order: Mapped[int] = mapped_column(Integer, nullable=False)

    geofence: Mapped["Geofence"] = relationship("Geofence", back_populates="points")
