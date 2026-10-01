from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_
from app.models.location_event import LocationEvent


class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, location_id: int) -> Optional[LocationEvent]:
        stmt = (
            select(LocationEvent)
            .options(joinedload(LocationEvent.device), joinedload(LocationEvent.user))
            .where(LocationEvent.id == location_id)
        )
        return self.db.scalars(stmt).first()

    def get_latest_by_device(self, device_id: int) -> Optional[LocationEvent]:
        stmt = (
            select(LocationEvent)
            .where(LocationEvent.device_id == device_id)
            .order_by(LocationEvent.timestamp.desc(), LocationEvent.id.desc())
        )
        return self.db.scalars(stmt).first()

    def check_duplicate(
        self,
        device_id: int,
        latitude: float,
        longitude: float,
        timestamp: datetime,
        window_seconds: int = 5,
    ) -> bool:
        """
        Check if an identical GPS reading for this device was recently stored within window_seconds.
        """
        start_time = timestamp - timedelta(seconds=window_seconds)
        end_time = timestamp + timedelta(seconds=window_seconds)

        stmt = select(LocationEvent).where(
            LocationEvent.device_id == device_id,
            LocationEvent.timestamp >= start_time,
            LocationEvent.timestamp <= end_time,
            func.abs(LocationEvent.latitude - latitude) < 1e-6,
            func.abs(LocationEvent.longitude - longitude) < 1e-6,
        )
        return self.db.scalars(stmt).first() is not None

    def create(self, location: LocationEvent) -> LocationEvent:
        self.db.add(location)
        self.db.flush()
        return location

    def list(
        self,
        skip: int = 0,
        limit: int = 50,
        device_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[LocationEvent], int]:
        stmt = select(LocationEvent).options(joinedload(LocationEvent.device), joinedload(LocationEvent.user))
        count_stmt = select(func.count(LocationEvent.id))

        filters = []
        if device_id:
            filters.append(LocationEvent.device_id == device_id)
        if user_id:
            filters.append(LocationEvent.user_id == user_id)
        if start_date:
            filters.append(LocationEvent.timestamp >= start_date)
        if end_date:
            filters.append(LocationEvent.timestamp <= end_date)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        total = self.db.scalar(count_stmt) or 0
        locations = list(
            self.db.scalars(
                stmt.order_by(LocationEvent.timestamp.desc(), LocationEvent.id.desc()).offset(skip).limit(limit)
            ).all()
        )
        return locations, total
