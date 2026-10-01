from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class GeofenceEvent(Base):
    __tablename__ = "geofence_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    geofence_id: Mapped[int] = mapped_column(ForeignKey("geofences.id", ondelete="CASCADE"), index=True, nullable=False)
    location_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location_events.id", ondelete="SET NULL"), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # "ENTER", "EXIT", "INSIDE", "OUTSIDE"
    previous_state: Mapped[str] = mapped_column(String(20), nullable=False)  # "INSIDE", "OUTSIDE", "UNKNOWN"
    current_state: Mapped[str] = mapped_column(String(20), nullable=False)   # "INSIDE", "OUTSIDE", "UNKNOWN"
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy_meters: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device: Mapped["Device"] = relationship("Device", back_populates="geofence_events")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="geofence_events")
    geofence: Mapped["Geofence"] = relationship("Geofence", back_populates="geofence_events")
    location_event: Mapped[Optional["LocationEvent"]] = relationship("LocationEvent", back_populates="geofence_events")

    __table_args__ = (
        Index("idx_geofence_event_dev_geo", "device_id", "geofence_id", "timestamp"),
        Index("idx_geofence_event_type_time", "event_type", "timestamp"),
    )
