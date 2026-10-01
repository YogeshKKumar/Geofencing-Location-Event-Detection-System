from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from app.models.device import Device
from app.models.user import User


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, device_id: int) -> Optional[Device]:
        stmt = select(Device).options(joinedload(Device.user)).where(Device.id == device_id)
        return self.db.scalars(stmt).first()

    def get_by_identifier(self, identifier: str) -> Optional[Device]:
        stmt = select(Device).options(joinedload(Device.user)).where(Device.device_identifier == identifier)
        return self.db.scalars(stmt).first()

    def get_for_update(self, device_id: int) -> Optional[Device]:
        """Lock device row for update to prevent concurrent race conditions"""
        # SQLite does not support with_for_update well, but MySQL does
        stmt = select(Device).where(Device.id == device_id)
        if self.db.bind and self.db.bind.dialect.name == "mysql":
            stmt = stmt.with_for_update()
        return self.db.scalars(stmt).first()

    def create(self, device: Device) -> Device:
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def update(self, device: Device) -> Device:
        self.db.commit()
        self.db.refresh(device)
        return device

    def update_location(self, device: Device, latitude: float, longitude: float, location_time: datetime) -> Device:
        device.last_latitude = latitude
        device.last_longitude = longitude
        device.last_location_at = location_time
        self.db.commit()
        self.db.refresh(device)
        return device

    def delete(self, device: Device) -> None:
        self.db.delete(device)
        self.db.commit()

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Device], int]:
        stmt = select(Device).options(joinedload(Device.user))
        count_stmt = select(func.count(Device.id))

        if user_id:
            stmt = stmt.where(Device.user_id == user_id)
            count_stmt = count_stmt.where(Device.user_id == user_id)

        if is_active is not None:
            stmt = stmt.where(Device.is_active == is_active)
            count_stmt = count_stmt.where(Device.is_active == is_active)

        if search:
            search_filter = (Device.name.ilike(f"%{search}%")) | (Device.device_identifier.ilike(f"%{search}%"))
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = self.db.scalar(count_stmt) or 0
        devices = list(self.db.scalars(stmt.order_by(Device.id.desc()).offset(skip).limit(limit)).all())
        return devices, total
