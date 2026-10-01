from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class LocationEvent(Base):
    __tablename__ = "location_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy_meters: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    device: Mapped["Device"] = relationship("Device", back_populates="location_events")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="location_events")
    geofence_events: Mapped[List["GeofenceEvent"]] = relationship(
        "GeofenceEvent",
        back_populates="location_event",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_location_device_time", "device_id", "timestamp"),
    )
